from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.genre import GenersService, get_genre_service
from src.core.constants import NOT_FOUND_MESS

router = APIRouter()

class Genre(BaseModel):
    id: str
    title: str

class Genres(BaseModel):
    result: list

@router.get('/', response_list=list)
async def genre_details(genre_service: GenersService = Depends(get_genre_service)) -> list:
    genres = await genre_service.get_by_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'genre {NOT_FOUND_MESS}')

    return Genres(result = genres)

@router.get('/{genre_id}', response_model=Genre)   
async def get_genre_by_id(genre_id, genre_service: GenersService = Depends(get_genre_service)):
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'genre {NOT_FOUND_MESS}')

    return Genre(**genre.dict())
