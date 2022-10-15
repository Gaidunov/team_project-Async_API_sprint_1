import os

from pydantic import BaseSettings

from .testdata import ES_MOVIES_MAPPING


class TestSettings(BaseSettings):
    es_host: str = os.environ['ELASTIC_URL']
    es_index: str = os.environ['ELASTIC_INDEX_TO_TEST']
    es_id_field: str = 'id'
    es_index_mapping: dict = ES_MOVIES_MAPPING
    service_url: str = os.environ.get('SERVICE_URL', 'http://127.0.0.1:80')
 

test_settings = TestSettings()