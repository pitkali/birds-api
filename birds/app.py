import falcon
from pymongo import MongoClient

from . import resources
from . import storage


def setup_routes(the_app, collection, resource):
    the_app.add_route("/birds", collection)
    the_app.add_route("/birds/{bird_id}", resource)


def setup(mongo_collection = None):
    if mongo_collection is None:
        # Evil database not ready for production
        client = MongoClient()
        db = client.birds
        mongo_collection = db.birds
    birds_storage = storage.MongoStorage(mongo_collection)
    bird_collection = resources.BirdCollection(birds_storage)
    bird_resource = resources.BirdResource(birds_storage)
    bird_app = falcon.API()

    setup_routes(bird_app, bird_collection, bird_resource)
    return bird_app
