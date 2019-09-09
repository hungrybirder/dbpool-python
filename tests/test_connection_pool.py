#!/usr/bin/env python

import logging
import random
import time

import threading

import pytest

from dbpool import (
    # PoolError,
    ConnectionPool,
    PoolOption,
)


logger = logging.getLogger(__name__)


def _work(pool: ConnectionPool, quit_event: threading.Event) -> None:
    while not quit_event.is_set():
        try:
            db_conn = pool.borrow_connection()
            time.sleep(random.random())
        except Exception as e:
            logger.error(e)
        else:
            db_conn.close()


class TestConnectionPool:
    # pylint: disable=no-self-use,too-few-public-methods,redefined-outer-name

    @staticmethod
    def get_pool(min_idle=1,
                 max_idle=20,
                 max_age=300.0,
                 check_idle_interval=60.0) -> ConnectionPool:
        config = {
            'host': 'localhost',
            'port': 3306,
            'username': 'tester',
            'password': 'Rae9nie3pheevoquai3aeh',
            'database': 'sbtest',
        }
        op = PoolOption(
            min_idle=min_idle,
            max_idle=max_idle,
            max_age_in_sec=max_age,
            check_idle_interval=check_idle_interval,
        )
        return ConnectionPool(op, **config)

    def test_create_connection_pool(self):
        pool = self.get_pool()
        assert pool
        pool.close()

    def test_create_connection_pool_with_wrong_password(self):
        wrong = {
            'host': '127.0.0.1',
            'port': 3306,
            'username': 'tester',
            'password': 'xxxx',
            'database': 'test',
        }
        from mysql.connector import Error as _MySQLError
        with pytest.raises(_MySQLError):
            # pylint: disable=unused-variable
            op = PoolOption(min_idle=1, max_idle=2)
            ConnectionPool(op, **wrong)

    def test_concurrency(self):
        pool = self.get_pool(4, 20, 60, 5)
        logger.debug('init pool, %s', pool)
        assert pool
        workers = []

        event1 = threading.Event()
        for _ in range(20):
            worker = threading.Thread(target=_work,
                                      args=(pool, event1))
            worker.setDaemon(True)
            workers.append(worker)
        for w in workers:
            w.start()

        for _ in range(3):
            time.sleep(10)
            logger.debug('workers are running, %s', pool)

        event1.set()

        for w in workers:
            w.join()

        workers.clear()

        time.sleep(10)

        event2 = threading.Event()
        for _ in range(20):
            worker = threading.Thread(target=_work,
                                      args=(pool, event2))
            worker.setDaemon(True)
            workers.append(worker)
        for w in workers:
            w.start()

        for _ in range(3):
            logger.debug('#2 workers are running, %s', pool)
            time.sleep(10)

        event2.set()

        for w in workers:
            w.join()

        workers.clear()

        for _ in range(10):
            time.sleep(8)
            logger.debug('#2 workers stopped, %s', pool)

        pool.close()
        logger.debug('after pool stopped, %s', pool)
