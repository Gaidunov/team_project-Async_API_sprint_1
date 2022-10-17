from http import HTTPStatus
from fastapi import Query

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic.schema import List, Dict

from src.services.film import FilmService, get_film_service
from src.core.constants import NOT_FOUND_MESS
from src.services.utils import pagination

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0


class Films(BaseModel):
    pagination: Dict
    result: List


@router.get('/{film_id}', response_model=Film)
async def get_movie_by_id(
                        film_id, 
                        film_service: FilmService = Depends(get_film_service),
                        ):
    """## Get movie title and imdb_rating by id"""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'film {NOT_FOUND_MESS}'
        )

    return Film(**film.dict())


@router.get('/search/')
async def search_movie_by_word(
                            search_word: str,
                            film_service: FilmService = Depends(get_film_service),
                            pagination: dict = Depends(pagination)

) -> Films:
    """## Search by the word in the title"""
    films = await film_service.get_by_search_word(
        search_word, **pagination
    )

    return Films(pagination=films['pagination'], result=films['result'])


@router.get('/')
async def get_all_movies(
        sort: str = Query(
        default='imdb_rating',
        regex='^-?(imdb_rating|title)',
        description='You can use only: imdb_rating, -imdb_rating'),
        film_service: FilmService = Depends(get_film_service),
        pagination: dict = Depends(pagination)
) -> Films:
    """
    ## Get all movies
    ### **sort**: "-imdb_rating" - show worst first, "imdb_rating" - show best first, 
    """
    films = await film_service.get_films(
        order_by=sort, **pagination
    )
    return Films(pagination=films['pagination'], result=films['result'])
