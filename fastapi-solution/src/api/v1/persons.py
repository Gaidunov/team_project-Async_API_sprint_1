from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.services.person import PersonService, get_person_service
from src.core.constants import NOT_FOUND_MESS

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
    """## Get person name, role and film_ids by id"""
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'film {NOT_FOUND_MESS}'
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
    """## Search person by the word in name"""
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
    page_size: int = Query(ge=1, le=100, default=10, alias='page[size]'),
    page_number: int = Query(default=0, ge=0, alias='page[number]'),
    sort: str = Query(
        default='id',
        regex='^-?(id)',
        description='You can use only: id, -id'),
    person_service: PersonService = Depends(get_person_service),
) -> Persons:
    """## List all persons"""
    films = await person_service.get_persons(
        page_size=page_size,
        page_number=page_number,
        order_by=sort
    )

    return Persons(
        pagination=films['pagination'],
        result=films['result']
    )
