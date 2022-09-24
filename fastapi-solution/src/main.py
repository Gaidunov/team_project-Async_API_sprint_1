import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1 import films
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
    pass

    # remove when separate elastic service implemented

    # redis.redis = await aioredis.create_redis_pool(
    #     (
    #         config.REDIS_HOST,
    #         config.REDIS_PORT
    #     ),
    #     minsize=10,
    #     maxsize=20,
    # )
    # elastic.es = AsyncElasticsearch(
    #     hosts=[
    #         f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'
    #     ]
    # )


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
