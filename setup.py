#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import re
# import os
#
from setuptools import setup
# from setuptools import setup, find_packages

# __AUTHOR__ = 'liyong'
# __AUTHOR_EMAIL__ = 'hungrybirder@gmail.com'

# here = os.path.abspath(os.path.dirname(__file__))
# with open(os.path.join(here, 'dbpool', '__init__.py')) as f:
#     version_pat = r'^__version__\s*=\s*[\'""]([^\'""]*)[\'""]'
#     version = re.search(version_pat, f.read(), re.MULTILINE).group(1)

# with open("README.rst", "r") as fh:
#     long_description = fh.read()
#


def main():
    setup(
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
    )


if __name__ == '__main__':
    main()
