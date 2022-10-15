import time
import os

from elasticsearch import Elasticsearch

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=os.environ['elastic_url'])
    while True:
        if es_client.ping():
            print('Elastic ok!')
            break
        time.sleep(1)
