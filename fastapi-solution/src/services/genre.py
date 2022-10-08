from functools import lru_cache
from typing import Optional, Union
import json

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from .utils import get_result

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenersService:
    GENRE_BY_ID_KEY_TEMPLATE = 'genre_id_{0}'
    SEARCH_GENRE_KEY_TEMPLATE = 'search_genre_query_params_{0}'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None

            await self._put_genre_to_cache(genre)
        return genre

    async def get_genres(
        self,
        page_size: int = 10,
        page_number: int = 0,
        order_by: str = 'id'
    ) -> Union[dict, None]:
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
                Genre
            )
        resp = await self.elastic.search(
            index='genres',
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
            Genre
        )

    async def _put_search_result_to_cache(
        self,
        key: str,
        search_result: str,
    ):
        await self.redis.set(
            self.SEARCH_GENRE_KEY_TEMPLATE.format(key),
            json.dumps(search_result),
            expire=GENRE_CACHE_EXPIRE_IN_SECONDS,
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
                'match': {
                    'title': {
                        'query': search_word
                    }
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
                Genre
            )
        resp = await self.elastic.search(
            index='genres',
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
            Genre
        )

    async def _get_search_result_from_cache(
        self,
        key: str,
    ) -> Union[dict, None]:
        data = await self.redis.get(
            self.SEARCH_GENRE_KEY_TEMPLATE.format(key)
        )
        if not data:
            return None

        return json.loads(data)
    
    async def _get_genre_from_elastic(
        self,
        genre_id: str
    ) -> Optional[Genre]:
        try:
            genre = await self.elastic.get(
                'genres',
                genre_id
            )
        except NotFoundError:
            return None

        return Genre(**genre['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(
            self.GENRE_BY_ID_KEY_TEMPLATE.format(genre_id)
        )
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            self.GENRE_BY_ID_KEY_TEMPLATE.format(genre.id),
            genre.json(),
            expire=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenersService:
    return GenersService(redis, elastic)
