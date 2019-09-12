#!/usr/bin/env python

import sys
import logging

from mysql.connector import Error

from dbpool import (
    ConnectionPool,
    PoolOption,
    PoolError,
)

logging.basicConfig()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    op = PoolOption(min_idle=2, max_idle=4)
    mysql_settings = {
        'host': 'localhost',
        'port': 3306,
        'username': 'tester',
        # 'password': 'Rae9nie3pheevo',
        'password': 'Rae9nie3pheevoquai3aeh',
        'database': 'sbtest',
    }
    try:
        pool = ConnectionPool(op, **mysql_settings)
    except Error as e:
        logger.error(e)
        sys.exit(1)

    db_conn = None
    try:
        db_conn = pool.borrow_connection()
        cur = db_conn.cursor()
        cur.execute('SELECT 123')
        print(cur.fetchall())
        cur.close()
        db_conn.close()
    except PoolError as e:
        logger.error(e)
        sys.exit(1)
    except Error as e:
        logger.error(e)
        sys.exit(1)

    pool.close()
