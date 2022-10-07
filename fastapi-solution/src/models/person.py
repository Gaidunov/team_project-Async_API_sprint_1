from .base_model import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: str
    name: str
    role: str
    film_ids: str
