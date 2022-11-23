from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.services.genre import GenersService, get_genre_service
from src.core.constants import NOT_FOUND_MESS
from src.services.utils import pagination
from src.auth import token_verification


router = APIRouter()


class Genre(BaseModel):
    id: str
    title: str


class Genres(BaseModel):
    pagination: dict
    result: list


@router.get('/', response_model=Genres)
@token_verification
async def get_all_genres(
    genre_service: GenersService = Depends(get_genre_service),
    pagination: dict = Depends(pagination)

) -> Genres:
    """## List all genres"""
    genres = await genre_service.get_genres(**pagination)
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'genre {NOT_FOUND_MESS}'
        )

    return Genres(
        pagination=genres['pagination'],
        result=genres['result']
    )


@router.get('/{genre_id}', response_model=Genre)   
@token_verification
async def get_genre_by_id(
    genre_id: str,
    genre_service: GenersService = Depends(get_genre_service)
):
    """## Get genre name by id"""
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'genre {NOT_FOUND_MESS}'
        )

    return Genre(**genre.dict())


@router.get('/search/')
@token_verification
async def search_genre_by_word(
    search_word: str,
    genre_service: GenersService = Depends(get_genre_service),
    pagination: dict = Depends(pagination)  
) -> Genres:
    """## Search genre by the word in the name"""
    genres = await genre_service.get_by_search_word(
        search_word, **pagination
    )

    return Genres(
        pagination=genres['pagination'],
        result=genres['result']
    )
