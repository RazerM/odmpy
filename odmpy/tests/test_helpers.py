import unittest

import odmpy.opm as opm


class TestHelpers(unittest.TestCase):
    def test_prefix(self):
        a = ['A', 'B', 'C', '']
        b = ['AA', 'AB', 'AC', 'A']
        for i, x in enumerate(opm.prefix('A', a)):
            self.assertEqual(b[i], x)

    def test_suffix(self):
        a = ['A', 'B', 'C', '']
        b = ['AA', 'BA', 'CA', 'A']
        for i, x in enumerate(opm.suffix('A', a)):
            self.assertEqual(b[i], x)

    def test_mant_exp(self):
        """Make sure it works."""
        self.assertEqual(opm._mant_exp(10), (1, 1))
        self.assertEqual(opm._mant_exp(0), (0, 0))

        m, e = opm._mant_exp(1.41e5)
        self.assertAlmostEqual(m, 1.41)
        self.assertEqual(e, 5)

        m, e = opm._mant_exp(0.000141)
        self.assertAlmostEqual(m, 1.41)
        self.assertEqual(e, -4)
