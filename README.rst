===============================
aiohttp_validate
===============================


.. image:: https://img.shields.io/pypi/v/aiohttp_validate.svg
        :target: https://pypi.python.org/pypi/aiohttp_validate

.. image:: https://img.shields.io/travis/dchaplinsky/aiohttp_validate.svg
        :target: https://travis-ci.org/dchaplinsky/aiohttp_validate

.. image:: https://readthedocs.org/projects/aiohttp-validate/badge/?version=latest
        :target: https://aiohttp-validate.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/dchaplinsky/aiohttp_validate/shield.svg
     :target: https://pyup.io/repos/github/dchaplinsky/aiohttp_validate/
     :alt: Updates


Simple library that helps you validate your API endpoints requests/responses with jsonschema_. Documentation is also available here at https://aiohttp-validate.readthedocs.io.



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

Features
--------
* The decorator to (optionally) validate the request to your aiohttp endpoint and it's response.
* Easily integrates with aiohttp_swaggerify_ to automatically document your endpoints with swagger.
* Validation errors are standardized and can be easily parsed by the clients of your service and also human-readable.


Developing
----------

Install requirement and launch tests::

    pip install -r requirements-dev.txt
    py.test


Credits
-------
That package is influenced by Tornado-JSON_ written by Hamza Faran 
Code to parse errors is written by `Ruslan Karalkin`_

License
-------

* Free software: MIT license

.. _jsonschema: http://json-schema.org/
.. _aiohttp_swaggerify: https://github.com/dchaplinsky/aiohttp_swaggerify
.. _Tornado-JSON: https://github.com/hfaran/Tornado-JSON/
.. _`Ruslan Karalkin`: https://github.com/rkaralkin
.. _`text tokenization microservice`: https://github.com/lang-uk/tokenize-ms
