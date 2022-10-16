from http import HTTPStatus
from typing import Callable

import pytest

from functional.settings import test_settings


@pytest.fixture()
def f_index_name() -> str:
    return 'person'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id_': '1'},
            {
                'status': HTTPStatus.OK,
                'ok_body': {
                    'film_ids': '1',
                    'id': '1',
                    'name': 'Jim Kerry',
                    'role': 'actor'
                }
            }
        ),
        (
            {'id_': '2'},
            {
                'status': HTTPStatus.NOT_FOUND,
                'ok_body': {'detail': 'film not found'}
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_person_by_id(
    query_data: dict,
    expected_answer: dict,
    es_write_data: Callable,
    make_get_request: Callable,
    delete_index: Callable,
) -> None:
    es_data = [{
        'id': 1,
        'name': 'Jim Kerry',
        'role': 'actor',
        'film_ids': '1',
    }]

    await es_write_data(es_data)
    search_url = test_settings.service_url + f'/api/v1/persons/{query_data["id_"]}'
    status, body = await make_get_request(search_url)

    assert expected_answer['status'] == status
    assert body == expected_answer['ok_body']

    await delete_index()


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'sorting': 'id'},
            {'status': HTTPStatus.OK, 'id': '19'}
        ),
        (
            {'sorting': '-id'},
            {'status': HTTPStatus.OK, 'id': '0'}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_all_persons(
    query_data: dict,
    expected_answer: dict,
    es_write_data: Callable,
    make_get_request: Callable,
    delete_index: Callable,
) -> None:
    es_data = [{
        'id': i,
        'name': f'Actor_{i}',
        'role': 'actor',
        'film_ids': '1',
    } for i in range(20)]

    await es_write_data(es_data)

    url = test_settings.service_url + f'/api/v1/persons/'
    params = {
        'page[size]': 10,
        'sort': query_data['sorting'],
        'page[number]': 0
    }

    status, body = await make_get_request(url, params)
    assert body['result'][0]['id'] == expected_answer['id']
    assert len(body['result']) == 10
    assert status == HTTPStatus.OK

    await delete_index()
