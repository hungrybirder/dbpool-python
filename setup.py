#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from setuptools import setup, find_packages

__AUTHOR__ = 'liyong'
__AUTHOR_EMAIL__ = 'hungrybirder@gmail.com'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'dbpool', '__init__.py')) as f:
    version_pat = r'^__version__\s*=\s*[\'""]([^\'""]*)[\'""]'
    version = re.search(version_pat, f.read(), re.MULTILINE).group(1)

with open("README.rst", "r") as fh:
    long_description = fh.read()


def main():
    setup(
        name='dbpool',
        description='Enhance mysql-connector-python pooling',
        long_description=long_description,
        url='https://github.com/hungrybirder/dbpool-python',
        version=version,
        author=__AUTHOR__,
        author_email=__AUTHOR_EMAIL__,
        maintainer=__AUTHOR__,
        maintainer_email=__AUTHOR_EMAIL__,
        packages=find_packages(exclude=['tests', 'examples']),
        license='MIT',
        zip_safe=False,
        install_requires=[
            'mysql-connector-python',
        ],
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
    )


if __name__ == '__main__':
    main()
