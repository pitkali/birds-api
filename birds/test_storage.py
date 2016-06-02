"""Storage engine sanity tests"""

from pymongo import MongoClient
import copy
import unittest
import time

from . import storage

ITEM_VISIBLE = {"key" : "valueA", storage.VISIBLE_KEY : True}
ITEM_HIDDEN  = {"key" : "valueB"}

def is_same_dictionary(a, b):
    """Shallow dictionary comparison"""
    keysA = set(a.keys())
    keysB = set(b.keys())
    sharedKeys = keysA & keysB
    if len(keysA) != len(keysB) or len(sharedKeys) != len(keysB):
        return False
    for k, v in a.items():
        if b[k] != v:
            return False
    return True


class ComparisonTest(unittest.TestCase):
    def test_same(self):
        self.assertTrue(is_same_dictionary(ITEM_VISIBLE, ITEM_VISIBLE))
        self.assertTrue(is_same_dictionary(ITEM_HIDDEN, ITEM_HIDDEN))

    def test_looks_same(self):
        self.assertTrue(is_same_dictionary({"key": "valueA"},
                                           {"key": "valueA"}))

    def test_different_key_count(self):
        self.assertFalse(is_same_dictionary(ITEM_VISIBLE, ITEM_HIDDEN))
        self.assertFalse(is_same_dictionary(ITEM_HIDDEN, ITEM_VISIBLE))

    def test_different_keys(self):
        self.assertFalse(is_same_dictionary({"keyA" : "value"},
                                            {"keyB" : "value"}))

    def test_different_values(self):
        self.assertFalse(is_same_dictionary({"key" : "valueA"},
                                            {"key" : "valueB"}))


def visible_item():
    return copy.deepcopy(ITEM_VISIBLE)

def hidden_item():
    return copy.deepcopy(ITEM_HIDDEN)


class AddFieldsTest(unittest.TestCase):
    def test_missing_both(self):
        item = hidden_item()
        storage.add_default_fields(item)
        self.assertIn(storage.VISIBLE_KEY, item)
        self.assertIn(storage.ADDED_KEY, item)
        self.assertFalse(item[storage.VISIBLE_KEY])

    def test_missing_date(self):
        item = visible_item()
        storage.add_default_fields(item)
        self.assertIn(storage.VISIBLE_KEY, item)
        self.assertIn(storage.ADDED_KEY, item)
        self.assertTrue(item[storage.VISIBLE_KEY])

    def test_date_format(self):
        item = visible_item()
        storage.add_default_fields(item)
        time.strptime(item[storage.ADDED_KEY],
                      "%Y-%m-%d")


class StorageTest(unittest.TestCase):
    """Tests the storage engine implementation for sanity."""

    def list(self):
        """Wraps storage listing returning list."""
        return list(self.storage.list())

    def test_store_retrieve(self):
        item = visible_item()
        self.assertTrue(is_same_dictionary(
            self.storage.retrieve(self.storage.store(item)),
            item))

    def test_stringified_id(self):
        item = visible_item()
        item_id = str(self.storage.store(item))
        self.assertTrue(is_same_dictionary(
            self.storage.retrieve(item_id), item))
        self.assertTrue(self.storage.remove(item_id))

    def test_store_remove(self):
        self.assertEqual(len(self.list()), 0)
        item_id = self.storage.store(visible_item())
        self.assertEqual(len(self.list()), 1)
        self.assertTrue(self.storage.remove(item_id))
        self.assertIsNone(self.storage.retrieve(item_id))
        self.assertEqual(len(self.list()), 0)

    def test_store_hidden(self):
        item = hidden_item()
        self.assertEqual(len(self.list()), 0)
        item_id = self.storage.store(item)
        self.assertEqual(len(self.list()), 0)
        self.assertTrue(
            is_same_dictionary(self.storage.retrieve(item_id), item))

    def test_list(self):
        self.storage.store(hidden_item())
        visible_item_id = self.storage.store(visible_item())
        l = self.list()
        self.assertEqual(visible_item_id, l[0])

    def test_retrieve_missing(self):
        self.assertIsNone(self.storage.retrieve("I'm so random"))

    def test_remove_missing(self):
        self.assertFalse(
            self.storage.remove("These are not the droids you're looking for"))


class MemoryStorageTest(StorageTest):
    def setUp(self):
        self.storage = storage.MemoryStorage()


MONGO_TEST_COLLECTION = "storage_test"

class MongoStorageTest(StorageTest):
    @classmethod
    def setUpClass(cls):
        # Wow, such default instance, much evil.
        cls.client = MongoClient()
        cls.db = cls.client.test_db
        # Make sure the first test starts with no collection
        cls.db.drop_collection(MONGO_TEST_COLLECTION)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def setUp(self):
        self.storage = storage.MongoStorage(
            MongoStorageTest.db[MONGO_TEST_COLLECTION])

    def tearDown(self):
        MongoStorageTest.db.drop_collection(MONGO_TEST_COLLECTION)


# Override test loading to skip test from storage test base class
# without skipping them in the subclasses.
def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in (AddFieldsTest, ComparisonTest,
                       MemoryStorageTest, MongoStorageTest):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

