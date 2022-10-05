from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.schema import List, Dict

from src.services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    name: str
    role: str
    film_ids: str


class Persons(BaseModel):
    pagination: dict
    result: list


@router.get('/{person_id}', response_model=Person)
async def get_person_by_id(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )

    return Person(**person.dict())


@router.get('/search/')
async def search_person_by_word(
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
    person_service: PersonService = Depends(get_person_service),
) -> Persons:
    persons = await person_service.get_by_search_word(
        search_word,
        page_size=page_size,
        page_number=page_number
    )

    return Persons(
        pagination=persons['pagination'],
        result=persons['result']
    )


@router.get('/')
async def get_all_persons(
    page_size: int = Query(ge=1, le=100, default=10),
    page_number: int = Query(default=0, ge=0),
    sort: str = Query(
        default='id',
        regex='^-?(id)',
        description='You can use only: id, -id'),
    person_service: PersonService = Depends(get_person_service),
) -> Persons:

    films = await person_service.get_persons(
        page_size=page_size,
        page_number=page_number,
        order_by=sort
    )

    return Persons(
        pagination=films['pagination'],
        result=films['result']
    )
