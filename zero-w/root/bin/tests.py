# -*- coding: utf-8 -*-

import unittest

from conv import *
from ceboConst import initCebo, IO_0

###############################################################################
class Test_calc_xticks(unittest.TestCase):

    def test_len_ticks_ts70(self):
        self.timestamps = list(range(70))
        x_ticks = calc_xticks(self.timestamps)
        self.assertTrue(len(x_ticks) in range(3,60))

    def test_len_ticks_ts2(self):
        self.timestamps = list(range(2))
        x_ticks = calc_xticks(self.timestamps)
        self.assertTrue(len(x_ticks) ==2)

    def test_len_ticks_ts57(self):
        self.timestamps = list(range(57))
        x_ticks = calc_xticks(self.timestamps)
        self.assertTrue(len(x_ticks) == 57)

    def test_len_ticks_ts1800(self):
        self.timestamps = list(range(1800))
        x_ticks = calc_xticks(self.timestamps)
        self.assertTrue(len(x_ticks) in range(30,65))


###############################################################################
class Test_CeboSim(unittest.TestCase):
    def setUp(self):
        self.gCebo = initCebo()

    def test_getInstance(self):
        self.assertTrue(self.gCebo)

    def test_function_read(self):
        ans = self.gCebo.device.read()
        self.assertTrue(isinstance(ans, list))

    def test_function_write(self):
        self.gCebo.dp0.write(3)

    def test_fake_IO(self):
        name = IO_0.name
        self.assertEqual(name, 'IO-0' )
        IO_0.on()

    def test_anal(self):
        ch = 1
        ans = self.gCebo.device.getSingleEndedInputs()[ch].read()
        self.assertEqual(ans, 99)


# ----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
