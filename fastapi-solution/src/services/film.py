import json
from functools import lru_cache
from typing import Optional, Union

from elasticsearch import NotFoundError
from fastapi import Depends

from src.db.async_search_engine import get_elastic_engine, AsyncSearchEngine
from src.db.async_cache_storage import get_redis, AsyncCacheStorage
from src.models.film import Film
from .utils import get_result

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    FILM_BY_ID_KEY_TEMPLATE = 'film_id_{0}'
    SEARCH_FILM_KEY_TEMPLATE = 'search_film_query_params_{0}'

    def __init__(
        self,
        cache: AsyncCacheStorage,
        search_engine: AsyncSearchEngine,
    ) -> None:
        self._cache = cache
        self._search_engine = search_engine

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None

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
        data = await self._get_search_result_from_cache(
            f'films_{str(elastic_query)}',
        )
        if data:
            return get_result(
                data,
                page_size,
                page_number,
                Film
            )
        resp = await self._search_engine.search(
            index='movies',
            body=elastic_query
        )
        await self._put_search_result_to_cache(
            f'films_{str(elastic_query)}',
            resp,
        )
        return get_result(
            resp,
            page_size,
            page_number,
            Film
        )

    async def get_by_search_word(
        self,
        search_word: str,
        page_size: int = 10,
        page_number: int = 0
    ):
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

        data = await self._get_search_result_from_cache(
            str(elastic_query)
        )
        if data:
            return get_result(data, page_size, page_number, Film)
        resp = await self._search_engine.search(
            index='movies',
            body=elastic_query
        )
        await self._put_search_result_to_cache(
            str(elastic_query),
            resp,
        )
        return get_result(resp, page_size, page_number, Film)

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            film = await self._search_engine.get(
                'movies',
                film_id
            )
        except NotFoundError:
            return None

        return Film(**film['_source'])

    async def _film_from_cache(
        self,
        film_id: str
    ) -> Optional[Film]:
        data = await self._cache.get(
            self.FILM_BY_ID_KEY_TEMPLATE.format(film_id)
        )
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _get_search_result_from_cache(
        self,
        key: str,
    ) -> Union[str, None]:
        data = await self._cache.get(
            self.SEARCH_FILM_KEY_TEMPLATE.format(key)
        )
        if not data:
            return None

        return json.loads(data.decode('utf-8'))

    async def _put_search_result_to_cache(
        self,
        key: str,
        search_result: str,
    ):
        await self._cache.set(
            self.SEARCH_FILM_KEY_TEMPLATE.format(key),
            json.dumps(search_result),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS,
        )

    async def _put_film_to_cache(self, film: Film):
        await self._cache.set(
            self.FILM_BY_ID_KEY_TEMPLATE.format(film.id),
            film.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
    cache: AsyncCacheStorage = Depends(get_redis),
    search_engine: AsyncSearchEngine = Depends(get_elastic_engine),
) -> FilmService:
    return FilmService(cache, search_engine)
