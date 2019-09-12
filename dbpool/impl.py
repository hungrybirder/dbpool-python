#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import queue
from typing import (
    NamedTuple,
    Optional,
)
import threading
import logging
import math

from mysql.connector import MySQLConnection

logger = logging.getLogger(__name__)


class PoolError(Exception):
    """Pool Error"""


class NoAvailableConnectionError(PoolError):
    """no available conneciton"""


class CreateConnectionError(PoolError):
    """When create new conneciton """


class TestConnectionError(PoolError):
    """test connection error"""


class PoolOption(NamedTuple):
    """

    Arguments:
        min_idle (int): Hold min idle connection count.
        max_idle (int): Hold max idle connection count.
        max_age_in_sec (float): When a connection expired, reconnect.
            Default: 300.0 seconds
        check_idle_interval (float): Check idle thread run interval time.
            Default: 60.0 seconds

    """
    min_idle: int
    max_idle: int
    max_age_in_sec: float = 300.0
    check_idle_interval: float = 60.0

    def check(self):
        if self.min_idle < 0:
            raise PoolError('min_idle should be greater than 0')
        if self.max_idle < self.min_idle:
            raise PoolError('max_idle shouble be granter than min_idle')


class ConnectionQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)

    def __contains__(self, item) -> bool:
        with self.mutex:
            return item in self.queue

    def remove(self, item) -> Optional:
        with self.mutex:
            try:
                self.queue.remove(item)
                return item
            except ValueError:
                return None

    def free_all(self) -> int:
        with self.mutex:
            free_cnt = 0
            for conn in self.queue:
                conn.discard_and_close()
                free_cnt += 1
            self.queue.clear()
            return free_cnt


class PooledConnection(MySQLConnection):
    """
    Inherit from ``mysql.connector.MySQLConnection``.

    Client should not create PooledConnection.

    Just call :py:meth:`dbpool.ConnectionPool.borrow_connection`.

    """

    def __init__(self, *args, **kwargs):
        self._pool = None
        super().__init__(*args, **kwargs)
        self._last_connected = time.time()

    def set_pool(self, pool: 'ConnectionPool') -> None:
        self._pool = pool

    def close(self) -> None:
        """
        Return this connection to the pool.
        """
        if not self._pool:
            super().close()
        else:
            self._pool.return_connection(self)

    def is_max_age_expired(self) -> bool:
        age = time.time() - self._last_connected
        return age > self._pool.option.max_age_in_sec

    def force_reconnect(self) -> None:
        try:
            self.reconnect(attempts=3, delay=0.1)
            self._last_connected = time.time()
        except Exception as e:
            super().close()  # 如何重连失败，则放弃这个连接
            raise e

    def discard_and_close(self) -> None:
        self._pool = None
        super().close()

    def test(self) -> bool:
        try:
            self.ping(reconnect=True, attempts=3, delay=0.1)
            self._last_connected = time.time()
            return True
        except Exception:
            return False


class ConnectionPool:
    #pylint: disable=too-many-instance-attributes
    def __init__(self, option: PoolOption, **kwargs):
        option.check()
        self._option = option
        self._lock = threading.RLock()
        self._closed = False
        self._idle_cnt = 0
        self._busy_cnt = 0
        self._idle = ConnectionQueue(option.max_idle)
        self._busy = ConnectionQueue(option.max_idle)
        for pname in ('pool_name', 'pool_size'):
            if pname in kwargs:
                del kwargs[pname]
        self._mysql_settings = kwargs
        # 建立最小核心连接
        with self._lock:
            count = self.option.min_idle
            for _ in range(count):
                self._idle.put(self._create_connection())
                self._idle_cnt += 1

        self._check_idle_event = threading.Event()
        thd = threading.Thread(
            target=self,
            daemon=True,
            name=f'Check idle thread, with option={option}',
        )
        thd.start()
        self._check_idle_thread = thd

    @property
    def option(self) -> PoolOption:
        return self._option

    @property
    def idle_cnt(self) -> int:
        with self._lock:
            return self._idle_cnt

    @property
    def busy_cnt(self) -> int:
        with self._lock:
            return self._busy_cnt

    def __call__(self, *args, **kwargs):
        while not self._check_idle_event.is_set():
            try:
                to = self.option.check_idle_interval
                if not self._check_idle_event.wait(timeout=to):
                    self.check_idle()
            except Exception as e:
                logger.error(e)

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def close(self):
        """
        Close the :py:class:`ConnectionPool`.
        Free idle connections.
        """
        with self._lock:
            self._closed = True
            self._check_idle_event.set()
        # 已经释放锁
        time.sleep(0.5)
        with self._lock:
            self._idle_cnt -= self._idle.free_all()

    def borrow_connection(self) -> PooledConnection:
        """
        Borrow one connection from pool.

        Returns:
            PooledConnection: The available connection.

        Raises:
            TestConnectionError: Test ping got error.
            CreateConnectionError: Create new connection failed.
            PoolError: When pool is closed.
            NoAvailableConnectionError: The pool is busy fully.

        """
        if self.is_closed():
            raise PoolError('ConnectionPool is closed!')
        try:
            idle_conn = self._idle.get_nowait()
        except queue.Empty:
            idle_conn = None
        if idle_conn:
            with self._lock:
                self._idle_cnt -= 1
            if idle_conn.is_max_age_expired():
                idle_conn.force_reconnect()
            if not idle_conn.test():
                idle_conn.discard_and_close()
                raise TestConnectionError()
            try:
                self._busy.put(idle_conn)
                with self._lock:
                    self._busy_cnt += 1
                return idle_conn
            except queue.Full as e:
                logger.error(e)
                raise e
        with self._lock:
            total_cnt = self._idle_cnt + self._busy_cnt
            if total_cnt >= self.option.max_idle:
                raise NoAvailableConnectionError('ConnectionPool is full!')
            try:
                new_conn = self._create_connection()
            except Exception as e:
                raise CreateConnectionError() from e
            if not new_conn.test():
                new_conn.discard_and_close()
                raise TestConnectionError()
            try:
                self._busy.put(new_conn)
                self._busy_cnt += 1
            except queue.Full as e:
                logger.error(e)
            return new_conn

    def _create_connection(self) -> PooledConnection:
        config = self._mysql_settings
        conn = PooledConnection(**config)
        conn.set_pool(self)
        return conn

    def return_connection(self, conn: PooledConnection) -> None:
        removed_conn = self._busy.remove(conn)
        if not removed_conn:
            logger.warning('Connection has already been returned?')
        else:  # 成功删除
            with self._lock:
                self._busy_cnt -= 1
                if self.is_closed():
                    conn.discard_and_close()
                    return
                if conn.is_max_age_expired():
                    conn.force_reconnect()
                try:
                    self._idle.put(conn)
                    self._idle_cnt += 1
                except queue.Full as e:
                    logger.error(e)
                    conn.discard_and_close()

    def check_idle(self) -> None:
        if self._idle.empty():
            return
        min_idle = self.option.min_idle
        with self._lock:
            free_cnt = self._idle_cnt - min_idle
        # if _idle queue needs to reduce ,at least free one idle conneciton
        remove_cnt = math.ceil(free_cnt * 0.1)
        if remove_cnt <= 0:
            return
        logger.info(f'Check idle on {self}, remove_cnt={remove_cnt}')
        while remove_cnt > 0:
            try:
                idle_conn = self._idle.get(timeout=1.0)
            except queue.Empty:
                # now _idle queue is empty
                # just quit check_idle
                break
            else:
                with self._lock:
                    idle_conn.discard_and_close()
                    self._idle_cnt -= 1
                    if self._idle_cnt - min_idle <= 0:
                        break
                remove_cnt -= 1

    def __repr__(self) -> str:
        mysql_settings = self._mysql_settings.copy()
        mysql_settings['password'] = 'xxxxxxxxxxxx'
        with self._lock:
            return (f'<ConnectionPool(option={self.option},'
                    f'mysql_settings={mysql_settings},'
                    f'idle_cnt={self._idle_cnt},'
                    f'idle_qsize={self._idle.qsize()},'
                    f'busy_cnt={self._busy_cnt},'
                    f'busy_qsize={self._busy.qsize()},'
                    f'closed={self._closed}'
                    f' at {hex(id(self))}>')
