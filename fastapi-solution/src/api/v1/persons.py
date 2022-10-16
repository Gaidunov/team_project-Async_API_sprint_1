from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.schema import List, Dict

from src.services.person import PersonService, get_person_service
from src.core.constants import NOT_FOUND_MESS
from src.services.utils import pagination


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
    pagination: dict = Depends(pagination),
    person_service: PersonService = Depends(get_person_service),
) -> Persons:
    """## Search person by the word in name"""
    persons = await person_service.get_by_search_word(
        search_word, **pagination
    )

    return Persons(
        pagination=persons['pagination'],
        result=persons['result']
    )


@router.get('/')
async def get_all_persons(
    pagination: dict = Depends(pagination),
    sort: str = Query(
        default='id',
        regex='^-?(id)',
        description='You can use only: id, -id'),
    person_service: PersonService = Depends(get_person_service),
) -> Persons:
    """## List all persons"""
    films = await person_service.get_persons(
        order_by=sort, **pagination
    )

    return Persons(
        pagination=films['pagination'],
        result=films['result']
    )
