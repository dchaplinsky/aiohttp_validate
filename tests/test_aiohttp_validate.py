#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aiohttp_validate
----------------------------------

Tests for `aiohttp_validate` module.
"""

import pytest

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

async def test_invalid_request(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_post('/', hello)
    app.router.add_get('/', hello)
    client = await test_client(app)

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

async def test_wrong_request_format(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_post('/', hello)
    client = await test_client(app)

    resp = await client.post('/', data='{"nottext": "foobar"}')
    assert resp.status == 400
    text = await resp.json()
    assert 'Request is invalid' in text["error"]
    assert text["errors"]

async def test_correct_request(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_post('/', hello)
    app.router.add_get('/', hello)
    client = await test_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text

    resp = await client.get('/', data='{"text": "foobar"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello world' in text

async def test_invalid_response(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_post('/', invalid_enc)
    app.router.add_get('/', invalid_enc)
    client = await test_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    assert resp.status == 500
    text = await resp.json()
    assert 'Response is malformed' in text["error"]

    resp = await client.get('/', data='{"text": "foobar"}')
    assert resp.status == 500
    text = await resp.json()
    assert 'Response is malformed' in text["error"]


async def test_wrong_response_format(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_post('/', validate_output)
    client = await test_client(app)

    resp = await client.post('/', data='{"text": "foobar"}')
    text = await resp.json()
    assert resp.status == 200
    assert text["text"] == "foobar"

    resp = await client.post('/', data='123')
    assert resp.status == 400
    text = await resp.json()
    assert "Request is invalid" in text["error"]
    assert text["errors"]
