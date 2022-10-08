import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings

@pytest.fixture
def es_write_data():
    async def inner(data: List[dict]):
        bulk_query = get_es_bulk_query(data, test_settings.es_index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'

        es_client = AsyncElasticsearch(hosts=test_settings.es_host, 
                                       validate_cert=False, 
                                       use_ssl=False)
        response = await es_client.bulk(str_query, refresh=True)
        await es_client.close()
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner