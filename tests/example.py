# -*- coding: utf-8 -*-

"""
How to run it:

::
    python setup.py test

You should see output something like this:

::

    running test
    running egg_info
    writing requirements to seismograph.egg-info/requires.txt
    writing seismograph.egg-info/PKG-INFO
    writing top-level names to seismograph.egg-info/top_level.txt
    writing dependency_links to seismograph.egg-info/dependency_links.txt
    writing entry points to seismograph.egg-info/entry_points.txt
    reading manifest file 'seismograph.egg-info/SOURCES.txt'
    writing manifest file 'seismograph.egg-info/SOURCES.txt'
    running build_ext
    test (tests.example.ExampleTestCase) ... Hello World!
    ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
"""

import unittest


class ExampleTestCase(unittest.TestCase):

    def test(self):
        print 'Hello World!'
