import json
from functools import lru_cache
from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import Person
from .utils import get_result

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    PERSON_BY_ID_KEY_TEMPLATE = 'person_id_{0}'
    SEARCH_PERSON_KEY_TEMPLATE = 'search_person_query_params_{0}'

    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch
    ) -> None:
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(
        self,
        person_id: str
    ) -> Optional[Person]:
        person = await self._person_from_cache(
            person_id
        )
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None

            await self._put_person_to_cache(person)
        return person

    async def get_persons(
        self,
        page_size: int = 10,
        page_number: int = 0,
        order_by: str = 'id'
    ):
        order = 'desc'
        if order_by.startswith('-'):
            order = 'asc'
            order_by = order_by[1:]

        elastic_query = {
            'size': page_size,
            'from': page_number * page_size,
            'sort': [
                {
                    order_by: {
                        'order': order,
                    }
                }
            ]
        }
        data = await self._get_search_result_from_cache(
            str(elastic_query),
        )
        if data:
            return get_result(
                data,
                page_size,
                page_number,
                Person
            )
        resp = await self.elastic.search(
            index='person',
            body=elastic_query
        )
        await self._put_search_result_to_cache(
            f'persons_{str(elastic_query)}',
            resp,
        )
        return get_result(
            resp,
            page_size,
            page_number,
            Person
        )

    async def _get_search_result_from_cache(
        self,
        key: str,
    ) -> Union[dict, None]:
        data = await self.redis.get(
            self.SEARCH_PERSON_KEY_TEMPLATE.format(key)
        )
        if not data:
            return None

        return json.loads(data)

    async def _put_search_result_to_cache(
        self,
        key: str,
        search_result: str,
    ):
        await self.redis.set(
            self.SEARCH_PERSON_KEY_TEMPLATE.format(key),
            json.dumps(search_result),
            expire=PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_by_search_word(
        self,
        search_word: str,
        page_size: int = 10,
        page_number: int = 0
    ) -> dict:
        elastic_query = {
            'size': page_size,
            'from': page_number * page_size,
            'query': {
                'multi_match': {
                    'query': search_word,
                    'fields': ['role', 'name']
                }
            }
        }
        data = await self._get_search_result_from_cache(
            str(elastic_query)
        )
        if data:
            return get_result(
                data,
                page_size,
                page_number,
                Person
            )
        resp = await self.elastic.search(
            index='person',
            body=elastic_query
        )
        await self._put_search_result_to_cache(
            str(elastic_query),
            resp,
        )
        return get_result(
            resp,
            page_size,
            page_number,
            Person
        )

    async def _get_person_from_elastic(
        self,
        person_id: str
    ) -> Optional[Person]:
        try:
            film = await self.elastic.get(
                'person',
                person_id
            )
        except NotFoundError:
            return None

        return Person(**film['_source'])

    async def _person_from_cache(
        self,
        person_id: str
    ) -> Optional[Person]:
        data = await self.redis.get(
            self.PERSON_BY_ID_KEY_TEMPLATE.format(person_id)
        )
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(
        self,
        person: Person,
    ) -> None:
        await self.redis.set(
            self.PERSON_BY_ID_KEY_TEMPLATE.format(person.id),
            person.json(),
            expire=PERSON_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
