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
    return item


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
        """Removes indicated item. Returns False if item_id is unknown."""
        raise NotImplementedError

    def list(self):
        """Generates sequence of visible items.

        Item is visible if it can be indexed with "visible" attribute
        and it results in true value."""
        raise NotImplementedError

    def parse_oid(self, item_id):
        """Parses potentially stringified ObjectID."""
        if isinstance(item_id, str):
            try:
                return ObjectId(item_id)
            except InvalidId:
                pass
        return item_id


class MemoryStorage(StorageEngine):
    """In-memory storage engine.

    Stores objects in memory without persistence. Mostly useful for testing."""

    def __init__(self):
        self.database = {}

    def store(self, item):
        add_default_fields(item)
        item_id = ObjectId()
        item[ID_KEY] = item_id
        self.database[item_id] = item
        return item_id

    def retrieve(self, item_id):
        item = self.database.get(self.parse_oid(item_id))
        return copy.deepcopy(item) if item else None

    def remove(self, item_id):
        """Removes indicated item. Raises KeyError if it's missing."""
        parsed_id = self.parse_oid(item_id)
        if not parsed_id in self.database:
            return False
        del self.database[self.parse_oid(item_id)]
        return True

    def list(self):
        """Generates sequence of visible items."""
        for key, item in self.database.items():
            if VISIBLE_KEY in item and item[VISIBLE_KEY]:
                yield key


class MongoStorage(StorageEngine):
    """Database storage for items."""

    def __init__(self, collection):
        self.collection = collection

    def retrieve(self, item_id):
        item = self.collection.find_one(self.parse_oid(item_id))
        if item:
            item[ID_KEY] = item["_id"]
        return item

    def list(self):
        cursor = self.collection.find({"visible" : True})
        for item in cursor:
            yield item["_id"]

    def remove(self, item_id):
        result = self.collection.delete_one({"_id" : self.parse_oid(item_id)})
        return False if result.deleted_count == 0 else True

    def store(self, item):
        add_default_fields(item)
        result = self.collection.insert_one(item)
        item[ID_KEY] = result.inserted_id
        return result.inserted_id