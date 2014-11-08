import unittest

import orbitdatamessages.opm as opm


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
