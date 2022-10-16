from fastapi import Query


def create_pagination(resp, page_size, page_number):
    total_entities_count = resp['hits']['total']['value']
    last_page = int(total_entities_count) // page_size - 1 if int(
        total_entities_count) % page_size == 0 else int(total_entities_count) // page_size
    next_page = page_number + 1 if page_number < last_page else None
    prev_page = page_number - 1 if (page_number - 1) >= 0 else None

    pagination_info = {'first': 0, 'last': last_page}

    if prev_page:
        pagination_info['prev'] = prev_page
    if next_page:
        pagination_info['next'] = next_page

    return {'pagination': pagination_info, 'result': []}


def get_result(resp, page_size, page_number, model):
    """парсим ответ от эластика"""
    result = create_pagination(resp, page_size, page_number)

    items = resp['hits']['hits']
    for item in items:
        result['result'].append(model(**item['_source']))

    return result


async def pagination(
    page_size: int = Query(ge=1, le=100, default=10, alias='page[size]'),
    page_number: int = Query(default=1, ge=0, alias='page[number]'),
    ):
    return {'page_size': page_size, 'page_number': page_number}


