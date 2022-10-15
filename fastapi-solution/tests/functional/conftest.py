import pytest
import aiohttp

import asyncio
import json
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from typing import List


@pytest.fixture()
def f_index_name() -> str:
    return 'movies'


@pytest.fixture
def event_loop(scope='session'):
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()


@pytest.fixture
async def make_get_request():
    async def inner(url, params=None): 
        async with aiohttp.ClientSession() as session: 
            async with session.get(url, params=params) as response:
                body = await response.json()       
                status = response.status
                return status, body 
                     
    return inner


@pytest.fixture(scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host)
    yield es_client
    await es_client.close()


def get_es_bulk_query(es_data, index, id_field):
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': index, '_id': row[id_field]}}),
            json.dumps(row)
        ])
    str_query = '\n'.join(bulk_query) + '\n'
    return str_query


@pytest.fixture
def es_write_data(es_client, f_index_name: str):
    async def inner(data: List[dict]):
        str_query = get_es_bulk_query(
            data,
            f_index_name,
            test_settings.es_id_field
        )
        response = await es_client.bulk(body=str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture
async def delete_index(f_index_name: str):
    async def inner():
        delete_url = test_settings.es_host + '/' + f_index_name
        async with aiohttp.ClientSession() as session: 
            async with session.delete(delete_url) as response:
                await response.json(content_type=None)
                print('удалили индекс', f_index_name)
    return inner
