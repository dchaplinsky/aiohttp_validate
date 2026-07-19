===============================
aiohttp_validate
===============================


.. image:: https://img.shields.io/pypi/v/aiohttp_validate.svg
        :target: https://pypi.python.org/pypi/aiohttp_validate

.. image:: https://github.com/dchaplinsky/aiohttp_validate/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/dchaplinsky/aiohttp_validate/actions/workflows/tests.yml


Simple library that helps you validate your API endpoints requests/responses with jsonschema_. Requires Python 3.9+ and aiohttp 3.8+.



Installation
------------
Install from PyPI::

    pip install aiohttp_validate

Usage
-----
Complete example of validation for `text tokenization microservice`_::

    from aiohttp_validate import validate

    @validate(
        request_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False
        },
        response_schema={
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    )
    async def tokenize_text_handler(request, *args):
        return tokenize_text(request["text"])

The wrapped handler receives the parsed and validated JSON body as its
first argument and the original aiohttp request object as the second::

    async def handler(data, request):
        pool = request.app["redis_pool"]  # the real request is right here
        ...

To respond with a status code other than 200, return a ``(data, status)``
tuple::

    async def create_handler(data, request):
        return {"id": new_id}, 201

The tuple form is detected by shape (a 2-tuple ending in an int), so if
your response data is itself such a tuple, return it as a list instead —
JSON has no tuples, the wire format is identical — or return a ready
``web.json_response``.

Features
--------
* The decorator to (optionally) validate the request to your aiohttp endpoint and it's response.
* Easily integrates with aiohttp_swaggerify_ to automatically document your endpoints with swagger.
* Validation errors are standardized and can be easily parsed by the clients of your service and also human-readable.


Developing
----------

Install with test dependencies and launch tests::

    pip install -e .[test]
    pytest


Credits
-------
That package is influenced by Tornado-JSON_ written by Hamza Faran 
Code to parse errors is written by `Ruslan Karalkin`_

Versioning
----------
This software follows `Semantic Versioning`_

.. _Semantic Versioning: http://semver.org/

License
-------

* Free software: MIT license

.. _jsonschema: http://json-schema.org/
.. _aiohttp_swaggerify: https://github.com/dchaplinsky/aiohttp_swaggerify
.. _Tornado-JSON: https://github.com/hfaran/Tornado-JSON/
.. _`Ruslan Karalkin`: https://github.com/rkaralkin
.. _`text tokenization microservice`: https://github.com/lang-uk/tokenize-ms
