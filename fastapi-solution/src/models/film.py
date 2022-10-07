from datetime import datetime
from .base_model import BaseOrjsonModel


class Film(BaseOrjsonModel):
    id: str
    title: str
    description: str
    created: datetime = None
    age_limit: int = None
    type: str = None
    imdb_rating: float
    genre: list
    director: list
    actors: list
    writers: list
