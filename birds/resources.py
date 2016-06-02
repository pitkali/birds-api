"""API resource classes"""
import json
import jsonschema
import logging
import falcon

from . import bird_schemas


def service_outage():
    raise falcon.HTTPServiceUnavailable(
        "Service outage",
        "Why is the rum gone? We'll be back as soon as the "
        "rum arrives.", 30)


EXPOSED_BIRD_ATTRIBUTES = ["id",
                           "name",
                           "family",
                           "continents",
                           "added",
                           "visible"]

def filter_dictionary(d, allowed_keys):
    return {k : v for k, v in d.items() if k in allowed_keys}

def dump_bird(bird):
    exposed_bird = filter_dictionary(bird, EXPOSED_BIRD_ATTRIBUTES)
    exposed_bird["id"] = str(exposed_bird["id"])
    return json.dumps(exposed_bird)


class BirdCollection(object):
    def __init__(self, storage):
        """Initialises collection resource.

        `storage' is the StorageEngine used."""
        self.storage = storage
        self.logger = logging.getLogger("birds-api")

    def on_get(self, req, resp):
        id_list = []
        try:
            id_list = list(map(str, self.storage.list()))
        except Exception as ex:
            self.logger.exception(ex)
            service_outage()

        resp.body = json.dumps(id_list)
        resp.status = falcon.HTTP_200

    def read_request_body(self, req):
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest("Empty request body",
                                        "A valid JSON document is required.")
        try:
            document = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest(
                "Malformed JSON",
                "Could not decode the request body. It was either not "
                "correctly formatted JSON document, or not encoded as "
                "UTF-8.")
        return document

    def on_post(self, req, resp):
        bird = self.read_request_body(req)
        try:
            jsonschema.validate(bird, bird_schemas.bird_input_schema)
        except jsonschema.ValidationError:
            raise falcon.HTTPBadRequest(
                "Incorrect bird data",
                "Supplied bird information does not conform to required "
                "schema.")
        bird_id = None
        try:
            bird_id = self.storage.store(bird)
        except Exception as ex:
            self.logger.exception(ex)
            service_outage()

        resp.body = dump_bird(bird)
        resp.status = falcon.HTTP_201
        resp.location = "/birds/" + str(bird_id)


class BirdResource(object):
    def __init__(self, storage):
        """Initialises bird resource with supplied StorageEngine"""
        self.storage = storage
        self.logger = logging.getLogger("birds-api")

    def on_get(self, req, resp, bird_id):
        bird = None
        try:
            bird = self.storage.retrieve(bird_id)
        except Exception as ex:
            self.logger.exception(ex)
            service_outage()
        if bird is None:
            raise falcon.HTTPNotFound()
        resp.body = dump_bird(bird)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, bird_id):
        removed = False
        try:
            removed = self.storage.remove(bird_id)
        except Exception as ex:
            self.logger.exception(ex)
            service_outage()
        if not removed:
            raise falcon.HTTPNotFound
        resp.status = falcon.HTTP_200