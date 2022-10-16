from typing import Optional
from aioredis import Redis
from abc import abstractmethod, ABC


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(
        self,
        key: str,
        **kwargs
    ) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
        expire: int,
        **kwargs
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def close(
        self,
        **kwargs
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def wait_closed(
        self,
        **kwargs
    ) -> None:
        raise NotImplementedError()


async_cache: Optional[AsyncCacheStorage] = None


class RedisCacheStorage(AsyncCacheStorage, Redis):
    ...


async def get_redis() -> AsyncCacheStorage:
    return async_cache
