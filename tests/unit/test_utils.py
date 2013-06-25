import unittest

from homefiles import utils


class CapitalizeFirstLetterTestCase(unittest.TestCase):
    def assertCapitalization(self, expected, s):
        self.assertEqual(expected, utils.capitalize_first_letter(s))

    def test_all_lower(self):
        self.assertCapitalization('Foo', 'foo')

    def test_all_upper(self):
        self.assertCapitalization('FOO', 'FOO')

    def test_mixed_case(self):
        self.assertCapitalization('FooBaR', 'fooBaR')
