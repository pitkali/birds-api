"""Birds storage engine

Abstracts away exact method/location of storing data from the rest of the
system, including persistence, ways to identify the resource, and the like."""

from bson.objectid import ObjectId, InvalidId
import copy
import time

VISIBLE_KEY = "visible"
ADDED_KEY = "added"
ID_KEY = "id"


def add_default_fields(item):
    if not VISIBLE_KEY in item:
        item[VISIBLE_KEY] = False
    if not ADDED_KEY in item:
        item[ADDED_KEY] = time.strftime("%Y-%m-%d", time.gmtime())


class StorageEngine(object):
    """Dysfunctional storage base class. Fails at everything.

    Note how methods accepting item ID need to be able to handle
    string representation of originally returned ID."""

    def store(self, item):
        """Stores `item' in the database, returning its identifier."""
        raise NotImplementedError

    def retrieve(self, item_id):
        """Retrieve item with given identifier, or None."""
        raise NotImplementedError

    def remove(self, item_id):
        """Removes indicated item. Raises KeyError if it's missing."""
        raise NotImplementedError

    def list(self):
        """Generates sequence of visible items.

        Item is visible if it can be indexed with "visible" attribute
        and it results in true value."""
        raise NotImplementedError


class MemoryStorage(StorageEngine):
    """In-memory storage engine.

    Stores objects in memory without persistence. Mostly useful for testing."""

    def __init__(self):
        self.next_id = 1
        self.database = {}

    def store(self, item):
        add_default_fields(item)
        item_id = self.next_id
        item[ID_KEY] = item_id
        self.next_id += 1
        self.database[item_id] = item
        return item_id

    def parse_id(self, item_id):
        if isinstance(item_id, str):
            try:
                return int(item_id)
            except:
                return -1
        return item_id

    def retrieve(self, item_id):
        item = self.database.get(self.parse_id(item_id))
        return copy.deepcopy(item) if item else None

    def remove(self, item_id):
        """Removes indicated item. Raises KeyError if it's missing."""
        del self.database[self.parse_id(item_id)]

    def list(self):
        """Generates sequence of visible items."""
        for key, item in self.database.items():
            if VISIBLE_KEY in item and item[VISIBLE_KEY]:
                yield key


class MongoStorage(StorageEngine):
    """Database storage for items."""

    def __init__(self, collection):
        self.collection = collection

    def parse_id(self, item_id):
        if isinstance(item_id, str):
            try:
                return ObjectId(item_id)
            except InvalidId:
                pass
        return item_id

    def retrieve(self, item_id):
        item = self.collection.find_one(self.parse_id(item_id))
        if item:
            item[ID_KEY] = item["_id"]
        return item

    def list(self):
        cursor = self.collection.find({"visible" : True})
        for item in cursor:
            yield item["_id"]

    def remove(self, item_id):
        result = self.collection.delete_one({"_id" : self.parse_id(item_id)})
        if result.deleted_count == 0:
            raise KeyError(item_id)

    def store(self, item):
        add_default_fields(item)
        result = self.collection.insert_one(item)
        item[ID_KEY] = result.inserted_id
        return result.inserted_id