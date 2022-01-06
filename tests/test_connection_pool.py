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
    logger.info("worker_%d starts", threading.current_thread().ident)
    while not quit_event.is_set():
        try:
            db_conn = pool.borrow_connection()
            time.sleep(random.random())
        except Exception as e:
            logger.error(e)
        else:
            db_conn.close()
    logger.info("worker_%d quits", threading.current_thread().ident)


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
        logger.info('init pool, %s', pool)
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
            time.sleep(5)
            logger.info('#1 workers are running, %s', pool)

        event1.set()

        for w in workers:
            w.join()

        logger.info("#1 all worker quit.")

        # workers.clear()
        workers = []

        event2 = threading.Event()
        for _ in range(20):
            worker = threading.Thread(target=_work,
                                      args=(pool, event2))
            worker.setDaemon(True)
            workers.append(worker)
        for w in workers:
            w.start()

        for _ in range(3):
            logger.info('#2 workers are running, %s', pool)
            time.sleep(5)

        event2.set()

        for w in workers:
            w.join()

        logger.info("#2 all worker quit.")

        workers.clear()

        db_conn = pool.borrow_connection()
        assert db_conn
        assert pool.busy_cnt > 0

        pool.close()
        assert pool.idle_cnt == 0

        logger.info('after pool stopped, %s', pool)
        db_conn.close()
        assert pool.busy_cnt == 0
        logger.info('#2. after pool stopped, %s', pool)
