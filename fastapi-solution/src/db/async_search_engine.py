from typing import Optional
from elasticsearch import AsyncElasticsearch
from abc import ABC, abstractmethod


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def search(
        self,
        index: str,
        body: dict,
        **kwargs
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def get(
        self,
        index: str,
        entity_id: str,
        **kwargs
    ) -> dict:
        raise NotImplementedError()

    @abstractmethod
    async def close(
        self,
        **kwargs
    ) -> dict:
        raise NotImplementedError()


async_search_engine: Optional[AsyncSearchEngine] = None


class AsyncElasticSearchEngine(AsyncSearchEngine, AsyncElasticsearch):
    ...


async def get_elastic_engine() -> AsyncSearchEngine:
    return async_search_engine
