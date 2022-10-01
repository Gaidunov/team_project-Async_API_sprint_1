from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film
from .result import get_result

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            # добавляем в кэш
            await self._put_film_to_cache(film)
        return film

    async def get_films(self, page_size: int = 10, page_number: int = 0, order_by: str = 'imdb_rating'):
        """фильмы с пагинацией, сортировка по рейтингу"""
        order = 'desc'
        if order_by.startswith('-'):
            order = 'asc'
            order_by = order_by[1:]

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "sort": [
                {
                    order_by: {
                        "order": order,
                    }
                }
            ]
        }

        resp = await self.elastic.search(index='movies', body=elastic_query)
        return get_result(resp, page_size, page_number, Film)

    async def get_by_search_word(self, search_word: str, page_size: int = 10, page_number: int = 0):
        """поиск по слову"""
        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "query": {
                "match": {
                    "title": {
                        "query": search_word
                    }
                }
            }
        }
        resp = await self.elastic.search(index='movies', body=elastic_query)

        return get_result(resp, page_size, page_number, Film)

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            film = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None

        print('взяли фильи НЕ из кеша')
        return Film(**film['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        print('взяли фильм из кэша')
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
