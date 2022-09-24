from turtle import st
import orjson

from pydantic import BaseModel

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Genre(BaseModel):
    id: str
    title: str
    imdb_rating: float

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps