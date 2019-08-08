#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbpool import get_version

def test_version():
    assert get_version() is not None
