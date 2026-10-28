from fastapi import Request, Response
from app import app
from datetime import date, datetime, time, timezone
from db import dbconn
from pydantic import BaseModel
from utils import constants
from utils.res_bodies import err
from utils.sessions import verify_requester

class CreateData(BaseModel):
    title: str
    description: str
    requirements: str
    destinationCountry: str
    initialDate: date | None
    finalDate: date | None

@app.post('/api/calls-for/create')
def create(
    req: Request,
    res: Response,
    data: CreateData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    trimmed_title = data.title.strip()
    trimmed_description = data.description.strip()
    trimmed_requirements = data.requirements.strip()

    if not 1 <= len(trimmed_title) <= 200:
        res.status_code = 400
        return err('El título debe contener entre 1 y 200 caracteres')

    initial_date_utc = (
        None if data.initialDate is None else
        datetime.combine(
            data.initialDate,
            time.min,
            tzinfo=timezone.utc
        )
    )
    final_date_utc = (
        None if data.finalDate is None else
        datetime.combine(
            data.finalDate,
            time.min,
            tzinfo=timezone.utc
        )
    )

    if (
        initial_date_utc and
        final_date_utc and
        initial_date_utc > final_date_utc
    ):
        res.status_code = 400
        return err('La fecha de apertura no puede ser mayor que la fecha de cierre')

    now = datetime.now(timezone.utc)
    conn = None
    