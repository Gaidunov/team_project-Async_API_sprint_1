import aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1 import films, persons, genres
from src.core import config
from src.db import async_cache_storage
from src.db import async_search_engine
from src.db.async_cache_storage import RedisCacheStorage
from src.db.async_search_engine import AsyncElasticSearchEngine

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis_dsn = config.RedisSettings().dict()
    redis_conn = await aioredis.create_redis_pool(
        address=(
            redis_dsn['host'],
            redis_dsn['port']
         ),
        password=redis_dsn['password'],
        minsize=10,
        maxsize=20,
    )
    async_cache_storage.async_cache = RedisCacheStorage(redis_conn)


    elastic_dsn = config.ElasticSearchSettings().dict()
    elastic_engine = AsyncElasticSearchEngine(
        hosts=[
            f'{elastic_dsn["host"]}:{elastic_dsn["port"]}'
        ]
    )
    async_search_engine.async_search_engine = elastic_engine


@app.on_event('shutdown')
async def shutdown():
    async_cache_storage.async_cache.close()
    await async_cache_storage.async_cache.wait_closed()
    await async_search_engine.async_search_engine.close()


app.include_router(
    films.router,
    prefix='/api/v1/films',
    tags=['films']
)

app.include_router(
    genres.router,
    prefix='/api/v1/genres',
    tags=['genres']
)

app.include_router(
    persons.router,
    prefix='/api/v1/persons',
    tags=['persons']
)
