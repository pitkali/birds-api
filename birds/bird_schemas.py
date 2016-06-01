bird_output_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GET /birds/{id} [response]",
    "description": "Get bird by id",
    "type": "object",
    "required": [
        "id",
        "name",
        "family",
        "continents",
        "added",
        "visible"
    ],
    "additionalProperties": False,
    "properties": {
        "id": {
            "type": "string",
            "description": "Object id from the database"
        },
        "name": {
            "type": "string",
            "description": "English bird name"
        },
        "family": {
            "type": "string",
            "description": "Latin bird family name"
        },
        "continents": {
            "type": "array",
            "description": "Continents the bird exist on",
            "minItems": 1,
            "items": { "type": "string" },
            "uniqueItems": True
        },
        "added": {
            "type": "string",
            "description": "Date the bird was added to the registry. Format YYYY-MM-DD"
        },
        "visible": {
            "type": "boolean",
            "description": "Determines if the bird should be visible in lists"
        }
    }
}

bird_list_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GET /birds [response]",
    "description": "List all visible birds in the registry",
    "type": "array",
    "additionalProperties": False,
    "items": {
        "type": "string",
        "description": "Object id",
        "uniqueItems": True
    }
}

bird_input_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "POST /birds [request]",
    "description": "Add a new bird to the library",
    "type": "object",
    "required": [
        "name",
        "family",
        "continents"
    ],
    "additionalProperties": False,
    "properties": {
        "name": {
            "type": "string",
            "description": "English bird name"
        },
        "family": {
            "type": "string",
            "description": "Latin bird family name"
        },
        "continents": {
            "type": "array",
            "description": "Continents the bird exist on",
            "minItems": 1,
            "items": { "type": "string" },
            "uniqueItems": True
        },
        "added": {
            "type": "string",
            "description": "Date the bird was added to the registry. Format YYYY-MM-DD"
        },
        "visible": {
            "type": "boolean",
            "description": "Determines if the bird should be visible in lists"
        }
    }
}

bird_added_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "POST /birds [response]",
    "description": "Add a new bird to the library",
    "type": "object",
    "required": [
        "id",
        "name",
        "family",
        "continents",
        "added",
        "visible"
    ],
    "additionalProperties": False,
    "properties": {
        "id": {
            "type": "string",
            "description": "Object id from the database"
        },
        "name": {
            "type": "string",
            "description": "English bird name"
        },
        "family": {
            "type": "string",
            "description": "Latin bird family name"
        },
        "continents": {
            "type": "array",
            "description": "Continents the bird exist on",
            "minItems": 1,
            "items": { "type": "string" },
            "uniqueItems": True
        },
        "added": {
            "type": "string",
            "description": "Date the bird was added to the registry. Format YYYY-MM-DD"
        },
        "visible": {
            "type": "boolean",
            "description": "Determines if the bird should be visible in lists"
        }
    }
}