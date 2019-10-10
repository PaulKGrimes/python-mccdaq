========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-mccdaq/badge/?style=flat
    :target: https://readthedocs.org/projects/python-mccdaq
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/paulkgrimes/python-mccdaq.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/paulkgrimes/python-mccdaq

.. |requires| image:: https://requires.io/github/paulkgrimes/python-mccdaq/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/paulkgrimes/python-mccdaq/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/paulkgrimes/python-mccdaq/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/paulkgrimes/python-mccdaq

.. |version| image:: https://img.shields.io/pypi/v/python-mccdaq.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/python-mccdaq

.. |wheel| image:: https://img.shields.io/pypi/wheel/python-mccdaq.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/python-mccdaq

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/python-mccdaq.svg
    :alt: Supported versions
    :target: https://pypi.org/project/python-mccdaq

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/python-mccdaq.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/python-mccdaq

.. |commits-since| image:: https://img.shields.io/github/commits-since/paulkgrimes/python-mccdaq/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/paulkgrimes/python-mccdaq/compare/v0.0.0...master



.. end-badges

A cross-platform wrapper library around MCC's uldaq and mccdaq libraries to provide a consistent interface on Windows
and Linux.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install python-mccdaq

You can also install the in-development version with::

    pip install https://github.com/paulkgrimes/python-mccdaq/archive/master.zip


Documentation
=============


https://python-mccdaq.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
