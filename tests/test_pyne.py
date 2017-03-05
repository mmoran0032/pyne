#!/usr/bin/env python3


import unittest

from .context import pyne


class TestPyne(unittest.TestCase):
    def setUp(self):
        self.b = pyne.buffer.Buffer('run270-13328.evt')
        self.b.f = open(self.b.filename, 'rb')

    def tearDown(self):
        self.b.f.close()

    def test_loading(self):
        pass
