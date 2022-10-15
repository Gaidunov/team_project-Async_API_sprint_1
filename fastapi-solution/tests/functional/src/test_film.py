import datetime
from typing import Callable
import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'id_': '1'},
                {'status': 200, 'ok_body': {'id': '1', 'title': 'The Star', 'imdb_rating': 8.5} }
        ),
        (
                {'id_': '2'},
                {'status': 404, 'ok_body': {'detail': 'film not found'}}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_by_id(
    query_data: dict,
    expected_answer: dict,
    es_write_data: Callable,
    make_get_request: Callable,
    delete_index: Callable,
) -> None:
    es_data = [{
        'id': 1,
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat(),
        'film_work_type': 'movie'
    }]
    
    await es_write_data(es_data)
    search_url = test_settings.service_url + f'/api/v1/films/{query_data["id_"]}'
    status, body = await make_get_request(search_url)
    
    assert expected_answer['status'] == status
    assert body == expected_answer['ok_body']

    await delete_index()


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'sorting': 'imdb_rating'},
            {'status': 200, 'rating': 19.0 }
        ),
        (
            {'sorting': '-imdb_rating'},
            {'status': 200, 'rating':0}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_all_films(
    query_data: dict,
    expected_answer: dict,
    es_write_data: Callable,
    make_get_request: Callable,
    delete_index: Callable,
) -> None:
    es_data = [{
        'id': i,
        'imdb_rating': i,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for i in range(20)]

    await es_write_data(es_data)

    url = test_settings.service_url + f'/api/v1/films/'
    params = {'page[size]': 10, 'sort': query_data['sorting'], 'page[number]': 0}

    status, body = await make_get_request(url, params)
    assert body['result'][0]['imdb_rating'] == expected_answer['rating']
    assert status == 200

    await delete_index()
