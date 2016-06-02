from bson.objectid import ObjectId
from copy import deepcopy
from jsonschema import validate, ValidationError
import json
import falcon.testing
import time
import unittest

from .app import setup_routes
from . import bird_schemas
from . import resources
from .storage import MemoryStorage, add_default_fields

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


A_BIRD = {
    "name" : "A Fancy Bird",
    "family" : "Birdies",
    "continents" : ["Europe"]
}

def default_bird():
    return deepcopy(A_BIRD)

def visible_bird():
    bird = default_bird()
    bird["visible"] = True
    return bird

def old_bird():
    bird = default_bird()
    bird["added"] = "1985-11-05"
    return bird

def today():
    return time.strftime("%Y-%m-%d", time.gmtime())


class SampleDataTest(unittest.TestCase):
    def test_validate_sample_data(self):
        schema = bird_schemas.bird_input_schema
        validate(default_bird(), schema)
        validate(visible_bird(), schema)
        validate(old_bird(), schema)


class BirdResourcesTest(falcon.testing.TestCase):
    def compare_stored_bird(self, birdA, birdB):
        for k in resources.EXPOSED_BIRD_ATTRIBUTES:
            self.assertEqual(str(birdA[k]), str(birdB[k]))

    def assertIsSubset(self, sub, sup):
        for k in sub.keys():
            self.assertEqual(str(sub[k]), str(sup[k]))

    @classmethod
    def setUpClass(cls):
        cls.bird_collection = resources.BirdCollection(MemoryStorage())
        cls.bird_resource = resources.BirdResource(MemoryStorage())

    def setUp(self):
        super(BirdResourcesTest, self).setUp()
        # Reset "database"
        self.storage = MemoryStorage()
        BirdResourcesTest.bird_collection.storage = self.storage
        BirdResourcesTest.bird_resource.storage = self.storage

        setup_routes(self.api,
                     BirdResourcesTest.bird_collection,
                     BirdResourcesTest.bird_resource)

    def test_empty_list(self):
        result = self.simulate_get("/birds")
        self.assertEqual(result.status_code, 200)
        validate(result.json, bird_schemas.bird_list_schema)
        self.assertEqual(len(result.json), 0)

    def test_list_with_hidden(self):
        self.storage.store(add_default_fields(default_bird()))
        result = self.simulate_get("/birds")
        self.assertEqual(result.status_code, 200)
        validate(result.json, bird_schemas.bird_list_schema)
        self.assertEqual(len(result.json), 0)

    def test_list_with_bird(self):
        bird = visible_bird()
        self.storage.store(add_default_fields(bird))
        result = self.simulate_get("/birds")
        self.assertEqual(result.status_code, 200)
        validate(result.json, bird_schemas.bird_list_schema)
        self.assertEqual(len(result.json), 1)
        self.assertEqual(result.json[0], str(bird["id"]))

    def test_add_simple_bird(self):
        bird = default_bird()
        result = self.simulate_post("/birds", body = json.dumps(bird))
        self.assertEqual(result.status_code, 201)
        stored_bird = result.json
        validate(stored_bird, bird_schemas.bird_added_schema)
        self.assertFalse(stored_bird["visible"])
        self.assertEqual(stored_bird["added"], today())

        backend_bird = self.storage.retrieve(stored_bird["id"])
        self.compare_stored_bird(stored_bird, backend_bird)
        self.assertIsSubset(bird, backend_bird)

    def test_add_visible_bird(self):
        bird = visible_bird()
        result = self.simulate_post("/birds", body = json.dumps(bird))
        self.assertEqual(result.status_code, 201)
        stored_bird = result.json
        validate(stored_bird, bird_schemas.bird_added_schema)
        self.assertTrue(stored_bird["visible"])
        self.assertEqual(stored_bird["added"], today())

    def test_add_old_bird(self):
        bird = old_bird()
        result = self.simulate_post("/birds", body = json.dumps(bird))
        self.assertEqual(result.status_code, 201)
        stored_bird = result.json
        validate(stored_bird, bird_schemas.bird_added_schema)
        self.assertIsSubset(bird, stored_bird)

    def test_add_invalid_bird(self):
        bird = visible_bird()
        bird["bogus-attribute"] = "Whoa! Hold your horses!"
        with self.assertRaises(ValidationError):
            validate(bird, bird_schemas.bird_input_schema)
        result = self.simulate_post("/birds", body = json.dumps(bird))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(len(list(self.storage.list())), 0)

    def test_add_no_bird(self):
        result = self.simulate_post("/birds")  # We've lost the body!
        self.assertEqual(result.status_code, 400)

    def test_get_missing_bird(self):
        some_id = ObjectId()
        result = self.simulate_get("/birds/" + str(some_id))
        self.assertEqual(result.status_code, 404)

    def test_get_hidden_bird(self):
        bird = default_bird()
        self.storage.store(add_default_fields(bird))
        result = self.simulate_get("/birds/" + str(bird["id"]))
        self.assertEqual(result.status_code, 200)
        stored_bird = result.json
        validate(stored_bird, bird_schemas.bird_output_schema)
        self.compare_stored_bird(stored_bird, bird)

    def test_delete_missing_bird(self):
        some_id = ObjectId()
        result = self.simulate_delete("/birds/" + str(some_id))
        self.assertEqual(result.status_code, 404)

    def test_delete_a_bird(self):
        bird = default_bird()
        self.storage.store(add_default_fields(bird))
        result = self.simulate_delete("/birds/" + str(bird["id"]))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(list(self.storage.list())), 0)