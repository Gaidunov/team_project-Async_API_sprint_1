from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenersService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            # добавляем в кэш
            await self._put_genre_to_cache(genre)
        return genre

    async def get_by_genres(self) -> list:
        genres = await self._all_genre_from_cache()
        if not genres:
            genres = await self._get_all_genre_from_elastic()
            if not genres:
                return None
            await self._put_all_genre_to_cache(genres)

        return genres

    async def _get_all_genre_from_elastic(self) -> list:
        try:
            doc = await self.elastic.get('genre')
        except NotFoundError:
            return None
        return doc['hits']['hits']

    async def _all_genre_from_cache(self) -> list:
        data = await self.redis.get('genres')
        if not data:
            return None
        return 
    
    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            genre = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None

        return Genre(**genre['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        print('взяли фильм из кэша')
        return genre
        
    async def _put_all_genre_to_cache(self, genres: list):
        await self.redis.set('genres', genres, expire=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.id, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenersService:
    return GenersService(redis, elastic)
