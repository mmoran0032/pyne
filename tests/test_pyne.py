#!/usr/bin/env python3


import unittest

from .context import pyne


class TestPyne(unittest.TestCase):
    def setUp(self):
        self.b = pyne.buffer.Buffer('run270-13328.evt')
        self.b = self.b.__enter__()

    def tearDown(self):
        self.b.__exit__(None, None, None)

    def test_loading(self):
        pass
