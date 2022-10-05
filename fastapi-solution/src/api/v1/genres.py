from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.services.genre import GenersService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    title: str


class Genres(BaseModel):
    pagination: dict
    result: list


@router.get('/', response_model=Genres)
async def genre_details(
    genre_service: GenersService = Depends(get_genre_service)
) -> Genres:
    genres = await genre_service.get_genres()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found'
        )
    logger.info('type', type=str(genres))

    return Genres(
        pagination=genres['pagination'],
        result=genres['result']
    )


@router.get('/{genre_id}', response_model=Genre)   
async def get_genre_by_id(
    genre_id: str,
    genre_service: GenersService = Depends(get_genre_service)
):
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found'
        )

    return Genre(**genre.dict())


@router.get('/search/')
async def search_genre_by_word(
    search_word: str,
    page_size: int = Query(
        ge=1,
        le=100,
        default=10
    ),
    page_number: int = Query(
        default=0,
        ge=0
    ),
    genre_service: GenersService = Depends(get_genre_service),
) -> Genres:
    genres = await genre_service.get_by_search_word(
        search_word,
        page_size=page_size,
        page_number=page_number
    )

    return Genres(
        pagination=genres['pagination'],
        result=genres['result']
    )
