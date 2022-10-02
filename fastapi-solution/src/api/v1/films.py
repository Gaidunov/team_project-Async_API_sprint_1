from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic.schema import List, Dict

from src.services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    """response model"""
    id: str
    title: str
    imdb_rating: float = 0

class Films(BaseModel):
    pagination: Dict
    result: List


@router.get('/{film_id}', response_model=Film)   
async def get_movie_by_id(film_id, film_service: FilmService = Depends(get_film_service)):
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(**film.dict())

@router.get('/search/')
async def search_movie_by_word(
        search_word: str,
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        film_service: FilmService = Depends(get_film_service),
) -> Films:
    films = await film_service.get_by_search_word(search_word, page_size=page_size, page_number=page_number)

    return Films(pagination=films['pagination'], result=films['result'])


@router.get('/')
async def get_all_movies(
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        sort: str = Query(
            default='imdb_rating',
            regex='^-?(imdb_rating|title)',
            description='You can use only: imdb_rating, -imdb_rating'),
        film_service: FilmService = Depends(get_film_service),
) -> Films:

    films = await film_service.get_films(page_size=page_size, page_number=page_number, order_by=sort)

    return Films(pagination=films['pagination'], result=films['result'])
