from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.genre import AllGeners, get_all_genres

router = APIRouter()

# class Genre(BaseModel):
#     id: str
#     name: str


@router.get('/genres/', response_list=list)
async def film_details(film_service: AllGeners = Depends(get_all_genres)) -> list:
    genres = await film_service.get_by_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')


    return genres


