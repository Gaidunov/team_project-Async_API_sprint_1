import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: str
    name: str
    role: str
    film_ids: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
