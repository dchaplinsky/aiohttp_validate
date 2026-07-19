"""Validate aiohttp request handlers' input and output with JSON schema."""

from __future__ import annotations

import functools
import inspect
import json
from collections import defaultdict
from typing import Any, NoReturn, Optional

from aiohttp import web
from aiohttp.abc import AbstractView
from jsonschema.validators import validator_for

__author__ = """Dmitry Chaplinsky"""
__email__ = "chaplinsky.dmitry@gmail.com"
__version__ = "2.0"

__all__ = ["validate"]


def _raise_exception(cls: type, reason: str, data: Any = None) -> NoReturn:
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


def _validate_data(data: Any, schema: dict, validator_cls: type) -> None:
    """
    Validate the dict against given schema (using given validator class).
    """
    validator = validator_cls(schema)
    _errors = defaultdict(list)

    def set_nested_item(dataDict, mapList, key, val):
        for _key in mapList:
            dataDict.setdefault(_key, {})
            dataDict = dataDict[_key]

        dataDict.setdefault(key, list())
        dataDict[key].append(val)

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
        if "required" in path or key == "required":
            key = err.message.split("'")[1]
        elif err.relative_path:
            key = err.relative_path.pop()

        set_nested_item(_errors, err.relative_path, key, err.message)

    if _errors:
        _raise_exception(
            web.HTTPBadRequest,
            "Request is invalid; There are validation errors.",
            _errors)


def validate(request_schema: Optional[dict] = None,
             response_schema: Optional[dict] = None):
    """
    Decorate request handler to make it automagically validate its request
    and response.

    The wrapped handler is called as ``handler(parsed_json, request)``
    (``handler(self, parsed_json, request)`` for class-based views) and may
    return either the response data, or a ``(data, status)`` tuple to set
    the response status code, or a ready ``StreamResponse`` (which skips
    response validation).

    Because the ``(data, status)`` form is detected by shape, response data
    that is itself a 2-tuple ending in an int must be returned as a list
    (JSON has no tuples anyway) or as a ready ``web.json_response``.
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

        func_is_coro = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def wrapped(*args):
            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                class_based = True
                request = args[0].request
            else:
                if func.__name__ != func.__qualname__:
                    class_based = True
                else:
                    class_based = False
                request = args[-1]

            # Strictly expect json object here
            try:
                req_body = await request.json()
            except (json.decoder.JSONDecodeError, TypeError):
                _raise_exception(
                    web.HTTPBadRequest,
                    "Request is malformed; could not decode JSON object.")

            # Validate request data against request schema (if given)
            if request_schema is not None:
                _validate_data(req_body, request_schema,
                               _request_schema_validator)

            coro_args = req_body, request
            if class_based:
                coro_args = (args[0],) + coro_args

            if func_is_coro:
                context = await func(*coro_args)
            else:
                context = func(*coro_args)

            # No validation of response for websockets stream
            if isinstance(context, web.StreamResponse):
                return context

            # Flask-style status sugar: a 2-tuple ending in an int (but
            # not a bool) means (data, status). Tuple-shaped response DATA
            # must be returned as a list instead (JSON arrays are lists
            # anyway), or as a ready json_response
            status = 200
            if isinstance(context, tuple) and len(context) == 2 and \
                    isinstance(context[1], int) and \
                    not isinstance(context[1], bool):
                context, status = context

            # Validate response data against response schema (if given)
            if response_schema is not None:
                _validate_data(context, response_schema,
                               _response_schema_validator)

            try:
                return web.json_response(context, status=status)
            except (TypeError,):
                _raise_exception(
                    web.HTTPInternalServerError,
                    "Response is malformed; could not encode JSON object.")

        # Store schemas in wrapped handlers, so it later can be reused
        setattr(wrapped, "_request_schema", request_schema)
        setattr(wrapped, "_response_schema", response_schema)
        return wrapped

    return wrapper
