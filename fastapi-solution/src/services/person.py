from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import Person
from .utils import get_result

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
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
            person = await self._get_film_from_elastic(person_id)
            if not person:
                return None

            await self._put_person_to_cache(person)
        return person

    async def get_films(
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

        resp = await self.elastic.search(
            index='person',
            body=elastic_query
        )
        return get_result(
            resp,
            page_size,
            page_number,
            Person
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
        resp = await self.elastic.search(
            index='person',
            body=elastic_query
        )

        return get_result(
            resp,
            page_size,
            page_number,
            Person
        )

    async def _get_film_from_elastic(
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
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(
        self,
        person: Person,
    ) -> None:
        await self.redis.set(
            person.id,
            person.json(),
            expire=PERSON_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
