import time
import os
import redis


if __name__ == '__main__':

    redis_client = redis.StrictRedis(
        host=os.environ['REDIS_HOST'],
        port=os.environ['REDIS_PORT'],
        password=os.environ['REDIS_PASSWORD'],
    )

    while True:
        if redis_client.ping():
            print('Redis ok!')
            break
        time.sleep(1)
