#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aiohttp_validate
----------------------------------

Tests for `aiohttp_validate` module.
"""

from datetime import datetime
from aiohttp_validate import validate
from aiohttp import web



@validate(
    request_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
        },
        "required": ["text"],
        "additionalProperties": False
    },
    response_schema=None,
)
async def hello(request, *args):
    return "Hello world!"


@validate(
    request_schema=None,
    response_schema=None,
)
async def invalid_enc(request, decoded):
    return datetime.now()


class HelloView(web.View):
    @validate(
        request_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False
        },
        response_schema=None,
    )
    async def get(self, data, request):
        return "Hello world!"

    @validate(
        request_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False
        },
        response_schema=None,
    )
    async def post(self, data, request):
        return "Hello world!"


@validate(
    request_schema=None,
    response_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
        },
        "required": ["text"],
        "additionalProperties": False
    }
)
async def validate_output(request, *args):
    return request


@validate(
    request_schema={
        "type": "object",
        "required": ["firstName", "nested"],
        "properties": {
            "firstName": {"type": "string"},
            "nested": {
                "type": "object",
                "required": ["test_for_nested"],
                "properties": {
                    "test_for_nested": {"type": "string"}
                }
            }
        }
    },
    response_schema=None,
)
async def validate_nested_errors(request, *args):
    return request


async def test_invalid_request(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', hello)
    app.router.add_get('/', hello)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert resp.status == 400
    text = await resp.json()
    assert 'Request is malformed' in text["error"]

    resp = await client.post('/')
    assert resp.status == 400
    text = await resp.json()
    assert 'Request is malformed' in text["error"]

    resp = await client.post('/', data="123afasdf")
    assert resp.status == 400
    text = await resp.json()
    assert 'Request is malformed' in text["error"]


async def test_wrong_request_format(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', hello)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"nottext": "foobar"}')
    assert resp.status == 400
    text = await resp.json()
    assert 'Request is invalid' in text["error"]
    assert text["errors"]


async def test_correct_request(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', hello)
    app.router.add_get('/', hello)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text

    resp = await client.get('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text


async def test_invalid_response(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', invalid_enc)
    app.router.add_get('/', invalid_enc)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    assert resp.status == 500
    text = await resp.json()
    assert 'Response is malformed' in text["error"]

    resp = await client.get('/', data='{"text": "foobar"}')
    assert resp.status == 500
    text = await resp.json()
    assert 'Response is malformed' in text["error"]


async def test_wrong_response_format(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', validate_output)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    text = await resp.json()
    assert resp.status == 200
    assert text["text"] == "foobar"

    resp = await client.post('/', data='123')
    assert resp.status == 400
    text = await resp.json()
    assert "Request is invalid" in text["error"]
    assert text["errors"]


async def test_class_based_valid_request(aiohttp_client):
    app = web.Application()
    app.router.add_view('/', HelloView)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text

    resp = await client.get('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text


async def test_nested_errors(aiohttp_client):
    app = web.Application()
    app.router.add_view('/', validate_nested_errors)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"nested": {}}')
    assert resp.status == 400
    text = await resp.json()

    # response for errors whould be like:
    # "errors": {
    #     "firstName": ["\'firstName\' is a required property"],
    #     "nested": {
    #         "test_for_nested": ["\'test_for_nested\' is a required property"]
    #     }
    # }
    errors = text["errors"]
    assert errors["firstName"]
    assert errors["nested"]["test_for_nested"]


@validate(
    request_schema={"type": "object"},
    response_schema=None,
)
async def created(request, *args):
    return {"id": 42}, 201


@validate(request_schema={"type": "object"})
def sync_handler(request, *args):
    return {"sync": True}


async def test_custom_status(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', created)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 201
    data = await resp.json()
    assert data["id"] == 42


async def test_sync_handler(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', sync_handler)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 200
    data = await resp.json()
    assert data["sync"] is True


class PlainAPI:
    """Not a web.View - exercises the qualname-based detection."""
    @validate(request_schema={"type": "object"})
    async def post(self, data, request):
        return {"plain_class": True}


@validate(request_schema=None)
async def passthrough(request, *args):
    return web.json_response({"raw": True}, status=418)


@validate(request_schema=None)
async def bool_tuple(request, *args):
    return {"flag": "x"}, True


@validate(request_schema=None)
async def tuple_data(request, *args):
    return ("a", "b")


async def test_type_mismatch_error_path(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', hello)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{"text": 123}')
    assert resp.status == 400
    text = await resp.json()
    assert text["errors"]["text"]


async def test_plain_class_method(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', PlainAPI().post)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 200
    data = await resp.json()
    assert data["plain_class"] is True


async def test_stream_response_passthrough(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', passthrough)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 418
    data = await resp.json()
    assert data["raw"] is True


async def test_bool_tuple_is_data_not_status(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', bool_tuple)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 200
    data = await resp.json()
    assert data == [{"flag": "x"}, True]


async def test_tuple_data_serialized_as_array(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', tuple_data)
    client = await aiohttp_client(app)

    resp = await client.post('/', data='{}')
    assert resp.status == 200
    data = await resp.json()
    assert data == ["a", "b"]
