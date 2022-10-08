import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic import BaseSettings

from src.core.logger import LOGGING

load_dotenv()

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')


class RedisSettings(BaseSettings):
    password: str
    host: str
    port: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "redis_"


class ElasticSearchSettings(BaseSettings):
    host: str
    port: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "elastic_"
