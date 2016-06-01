import jsonschema
import falcon.testing
import unittest

from . import bird_schemas
from . import resources

class FilderDictionaryTest(unittest.TestCase):
    def test_remove_extra(self):
        allowed_key = "key"
        not_allowed = "totally-not-allowed-attribute"
        value = "value"
        od = {allowed_key : value}
        od[not_allowed] = "not-a-value"

        d = resources.filter_dictionary(od, [allowed_key])
        self.assertIn(allowed_key, d, "Preserved original key?")
        self.assertNotIn(not_allowed, d, "Removed extraneous key?")
        self.assertEqual(d[allowed_key], value, "Preserved value?")

    def test_empty(self):
        allowed_key = "key"
        d = resources.filter_dictionary({}, [allowed_key])
        self.assertNotIn(allowed_key, d, "Didn't add allowed key?")

# TODO: need to test resources against schemas

