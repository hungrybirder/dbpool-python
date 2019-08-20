#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution

from dbpool.impl import (
    PoolOption,
    PooledConnection,
    ConnectionPool,
    PoolError,
)

__all__ = (
    'PoolOption',
    'PooledConnection',
    'ConnectionPool',
    'PoolError',
    'get_version',
)

def get_version() -> str:
    dist = get_distribution('dbpool')
    return dist.version
