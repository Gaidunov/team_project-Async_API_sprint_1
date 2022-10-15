import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.core.config import ElasticSearchSettings, RedisSettings
from src.api.v1 import films, persons, genres
from src.core import config
from src.db import elastic, redis


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis_dsn = RedisSettings().dict()
    redis.redis = await aioredis.create_redis_pool(
        address=(
            redis_dsn['host'],
            redis_dsn['port']
         ),
        password=redis_dsn['password'],
        minsize=10,
        maxsize=20,
    )

    elastic_dsn = ElasticSearchSettings().dict()
    elastic.es = AsyncElasticsearch(
        hosts=[
            f'{elastic_dsn["host"]}:{elastic_dsn["port"]}'
        ]
    )


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


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
