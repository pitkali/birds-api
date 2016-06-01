Overview
========
In this test you will be creating a basic HTTP service with a JSON API. The service you will build is a bird registry and it will support the following requests:

 - `GET /birds` - List all birds
 - `POST /birds` - Add a new bird
 - `GET /birds/{id}` - Get details on a specific bird
 - `DELETE /birds/{id}` - Delete a bird by id

No update method is required.

Purpose
=======

The purpose of this test is to see how the developer implements a basic API with a NoSQL database. We are looking at overall code quality and implementation strategy. Also error handling etc is of interest.

Requirements
============

 - You should use MongoDB as your database. We expect to find it on the
 default port `27017`
 - Write this in the language you feel most comfortable with
 - Any web framework is accepted
 - Document how to build and run your application
 - Document how to run the test suite

Delivery
========

Create a public repo on [GitHub](http://github.com) and post the code there. We will review the `master` branch.

Send an email to [adam@saltside.se](mailto: adam@saltside.se) when done.

API specification
=================

Add bird
--------

### Request `POST /birds`

The body is a JSON object based on the JSON schema can be found in `post-birds-request.json`.

 - If `visible` is not set, it should default to `false`.
 - `added` should default to today's date (in UTC)

### Response

Valid status codes:

 - `201 Created` if the bird was successfully added
 - `400 Bad request` if any mandatory fields were missing or if the input JSON was invalid

The body is a JSON object based on the JSON schema can be found in `post-birds-response.json`.

List all birds
--------------

### Request `GET /birds`

Empty body.

### Response

Valid status codes:

 - `200 OK`

The body is a JSON array based on the JSON schema can be found in `get-birds-response.json`.

Get bird by id
--------------

### Request `GET /birds/{id}`

Empty body.

### Response

Valid status codes:

 - `200 OK` if the bird exists
 - `404 Not found` if the bird does not exist

A `404 Not found` is expected when the bird does not exist. Birds with `visible` set to `false` should be returned with a `200 OK`.

The response body for a `200 OK` request can be found in `get-birds-id-response.json`.

Delete bird by id
-----------------

### Request `DELETE /birds/{id}`

Empty body

### Response

Valid status codes:

 - `200 OK` if the bird has been removed
 - `404 Not found` if the bird didn't exist

Empty body expected.
