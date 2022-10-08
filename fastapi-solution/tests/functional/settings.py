from pydantic import BaseSettings, ...


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    es_index: str = 
    es_id_field: str = 
    es_index_mapping: dict = 

    redis_host: str = 
    service_url: str =
 

test_settings = TestSettings()