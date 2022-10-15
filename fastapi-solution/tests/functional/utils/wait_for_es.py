import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from src.core.config import ElasticSearchSettings

load_dotenv()


if __name__ == '__main__':
    elastic_dsn = ElasticSearchSettings().dict()

    es_client = Elasticsearch(
        hosts=f'{elastic_dsn["host"]}:{elastic_dsn["port"]}',
        validate_cert=False,
        use_ssl=False
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
