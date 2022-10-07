from .base_model import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float = 0.0
