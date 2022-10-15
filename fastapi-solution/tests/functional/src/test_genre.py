import uuid
from typing import Callable

import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


@pytest.fixture()
def f_index_name() -> str:
    return 'genres'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'sorting': 'imdb_rating'},
            {'status': 200, 'rating': 8.5}
        ),
        (
            {'sorting': '-imdb_rating'},
            {'status': 200, 'rating': 8.5}
        )
    ]
)
@pytest.mark.asyncio
async def test_all_genre(
    es_write_data: Callable,
    make_get_request: Callable,
    query_data: dict,
    expected_answer: dict,
    es_client: AsyncElasticsearch,
    delete_index: Callable,
) -> None:
    es_data = [{
        'id': str(uuid.uuid4()),
        'title': 'The Star',
        'imdb_rating': 8.5,
    } for _ in range(10)]
     
    await es_write_data(es_data)
    url = test_settings.service_url + f'/api/v1/genres/'
    params = {'page[size]': 10, 'sort': query_data['sorting'], 'page[number]': 0}

    status, body = await make_get_request(url, params)
    assert body['result'][0]['imdb_rating'] == expected_answer['rating']
    assert status == 200

    await delete_index()


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id_': '1'},
            {'status': 200, 'ok_body': {'id': '1', 'title': 'LaLaLa', 'imdb_rating': 8.5} }
        ),
        (
            {'id_': '2'},
            {'status': 404, 'ok_body': {'detail': 'genre not found'}}
        )
    ]
)
@pytest.mark.asyncio
async def test_genre_on_id(
    es_write_data: Callable,
    make_get_request: Callable,
    query_data: dict,
    expected_answer: dict,
    es_client: AsyncElasticsearch,
    delete_index: Callable,
) -> None:
    id_uid = str(uuid.uuid4())
    es_data = {
        'id': id_uid,
        'title': 'LaLaLa',
        'imdb_rating': 8.5
    }
    await es_write_data(es_data)
    search_url = test_settings.service_url + f'/api/v1/films/genres/{id_uid}'
    status, body = await make_get_request(search_url, query_data)

    assert expected_answer['status'] == status
    assert expected_answer['length'] == len(body['result'])

    await delete_index()
