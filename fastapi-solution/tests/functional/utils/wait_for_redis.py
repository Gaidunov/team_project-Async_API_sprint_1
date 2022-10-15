import time

import redis
from dotenv import load_dotenv

from src.core.config import RedisSettings

load_dotenv()

if __name__ == '__main__':
    redis_dsn = RedisSettings().dict()

    redis_client = redis.StrictRedis(
        host=redis_dsn['host'],
        port=redis_dsn['port'],
        password=redis_dsn['password'],
    )

    while True:
        if redis_client.ping():
            break
        time.sleep(1)
