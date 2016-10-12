import json
import functools
import asyncio
from collections import defaultdict

from aiohttp import web
from aiohttp.abc import AbstractView
from jsonschema.validators import validator_for

__author__ = """Dmitry Chaplinsky"""
__email__ = 'chaplinsky.dmitry@gmail.com'
__version__ = '0.1.1'


def _raise_exception(cls, reason, data=None):
    """
    Raise aiohttp exception and pass payload/reason into it.
    """
    text_dict = {
        "error": reason
    }

    if data is not None:
        text_dict["errors"] = data

    raise cls(
        text=json.dumps(text_dict),
        content_type="application/json"
    )


def _validate_data(data, schema, validator_cls):
    """
    Validate the dict against given schema (using given validator class).
    """
    validator = validator_cls(schema)
    _errors = defaultdict(list)
    for err in validator.iter_errors(data):
        path = err.schema_path

        # Code courtesy: Ruslan Karalkin
        # Looking in error schema path for
        # property that failed validation
        # Schema example:
        # {
        #    "type": "object",
        #    "properties": {
        #        "foo": {"type": "number"},
        #        "bar": {"type": "string"}
        #     }
        #    "required": ["foo", "bar"]
        # }
        #
        # Related err.schema_path examples:
        # ['required'],
        # ['properties', 'foo', 'type']

        if "properties" in path:
            path.remove("properties")
        key = path.popleft()

        # If validation failed by missing property,
        # then parse err.message to find property name
        # as it always first word enclosed in quotes
        if key == "required":
            key = err.message.split("'")[1]

        _errors[key].append(str(err))

    if _errors:
        _raise_exception(
            web.HTTPBadRequest,
            "Request is invalid; There are validation errors.",
            _errors)


def validate(request_schema=None, response_schema=None):
    """
    Decorate request handler to make it automagically validate it's request
    and response.
    """
    def wrapper(func):
        # Validating the schemas itself.
        # Die with exception if they aren't valid
        if request_schema is not None:
            _request_schema_validator = validator_for(request_schema)
            _request_schema_validator.check_schema(request_schema)

        if response_schema is not None:
            _response_schema_validator = validator_for(response_schema)
            _response_schema_validator.check_schema(response_schema)

        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)

            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]

            # Strictly expect json object here
            try:
                req_body = yield from request.json()
            except (json.decoder.JSONDecodeError, TypeError):
                _raise_exception(
                    web.HTTPBadRequest,
                    "Request is malformed; could not decode JSON object.")

            # Validate request data against request schema (if given)
            if request_schema is not None:
                _validate_data(req_body, request_schema,
                               _request_schema_validator)

            context = yield from coro(req_body, request)

            # No validation of response for websockets stream
            if isinstance(context, web.StreamResponse):
                return context

            # Validate response data against response schema (if given)
            if response_schema is not None:
                _validate_data(context, response_schema,
                               _response_schema_validator)

            try:
                return web.json_response(context)
            except (TypeError, ):
                _raise_exception(
                    web.HTTPInternalServerError,
                    "Response is malformed; could not encode JSON object.")

        # Store schemas in wrapped handlers, so it later can be reused
        setattr(wrapped, "_request_schema", request_schema)
        setattr(wrapped, "_response_schema", response_schema)
        return wrapped
    return wrapper

__ALL__ = ["validate", "__author__", "__email__", "__version__"],
