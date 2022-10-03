from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class AllGeners:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_genres(self) -> list:
        genres = await self._film_from_cache()
        if not genres:
            genres = await self._get_film_from_elastic()
            if not genres:
                return None
            await self._put_film_to_cache(genres)

        return genres

    async def _get_film_from_elastic(self) -> list:
        try:
            doc = await self.elastic.get('genre')
        except NotFoundError:
            return None
        return doc['hits']['hits']

    async def _genre_from_cache(self) -> list:
        data = await self.redis.get('genres')
        if not data:
            return None
        return data

    async def _put_film_to_cache(self, genres: list):
        await self.redis.set('genres', genres, expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_all_genres(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> AllGeners:
    return AllGeners(redis, elastic)
