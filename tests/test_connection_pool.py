#!/usr/bin/env python

import pytest

import threading

from dbpool import (
    PoolError,
    ConnectionPool,
    PoolOption,
)


class TestConnectionPool:
    # pylint: disable=no-self-use,too-few-public-methods,redefined-outer-name

    @staticmethod
    def get_pool(min_idle=1, max_idle=20) -> ConnectionPool:
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
