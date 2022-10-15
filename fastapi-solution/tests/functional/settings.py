import os

from pydantic import BaseSettings


class TestSettings(BaseSettings):
    es_host: str = os.environ['ELASTIC_URL']
    es_id_field: str = 'id'
    service_url: str = os.environ.get('SERVICE_URL', 'http://127.0.0.1:80')
 

test_settings = TestSettings()
