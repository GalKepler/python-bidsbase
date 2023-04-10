========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-bidsbase/badge/?style=flat
    :target: https://python-bidsbase.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/galkepler/python-bidsbase/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/galkepler/python-bidsbase/actions

.. |codecov| image:: https://codecov.io/gh/galkepler/python-bidsbase/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/galkepler/python-bidsbase

.. |version| image:: https://img.shields.io/pypi/v/bidsbase.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/bidsbase

.. |wheel| image:: https://img.shields.io/pypi/wheel/bidsbase.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/bidsbase

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/bidsbase.svg
    :alt: Supported versions
    :target: https://pypi.org/project/bidsbase

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/bidsbase.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/bidsbase

.. |commits-since| image:: https://img.shields.io/github/commits-since/galkepler/python-bidsbase/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/galkepler/python-bidsbase/compare/v0.0.0...main



.. end-badges

A BIDS manager for The Base scanning protocol(s)

* Free software: BSD 2-Clause License

Installation
============

::

    pip install bidsbase

You can also install the in-development version with::

    pip install https://github.com/galkepler/python-bidsbase/archive/main.zip


Documentation
=============


https://python-bidsbase.readthedocs.io/


Development
===========

To run all the tests run::

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
