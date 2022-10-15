
import os
import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings

#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 

    
@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search_word': 'The Star'},
                {'length': 10, 'status':200}
        ),
        (
                {'search_word': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(es_write_data, make_get_request, query_data, expected_answer, es_client, delete_index):

    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
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
    } for _ in range(60)]

    # загружаем в ES    
    await es_write_data(es_data)
    # 3. Запрашиваем данные из ES по API
    search_url = test_settings.service_url + '/api/v1/films/search/'
    status, body = await make_get_request(search_url, query_data)

    assert expected_answer['status'] == status
    assert expected_answer['length'] == len(body['result'])
    
    #удалили индекс для чистоты эксперимента
    await delete_index()



