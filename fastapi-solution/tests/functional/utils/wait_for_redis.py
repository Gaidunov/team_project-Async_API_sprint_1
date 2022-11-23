import os

import redis

import functional.utils.utils as utils


@utils.backoff(
    exception_to_check=redis.ConnectionError
)
def ping_redis(
    client: redis.StrictRedis
) -> None:
    if client.ping():
        return


if __name__ == '__main__':
    redis_client = redis.StrictRedis(
        host=os.environ['REDIS_HOST'],
        port=int(os.environ['REDIS_PORT']),
        password=os.environ['REDIS_PASSWORD'],
    )

    ping_redis(redis_client)
