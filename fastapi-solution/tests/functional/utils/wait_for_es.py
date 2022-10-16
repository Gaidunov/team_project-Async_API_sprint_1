import os

from elasticsearch import Elasticsearch, ConnectionError

import functional.utils.utils as utils


@utils.backoff(
    exception_to_check=ConnectionError
)
def ping_elastic(
    client: Elasticsearch
) -> None:
    if client.ping():
        return


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=os.environ['elastic_url'])

    ping_elastic(es_client)
