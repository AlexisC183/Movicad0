from fastapi import Request, Response
from app import app
from db import dbconn
from pydantic import BaseModel
from functools import partial
from utils import constants
from utils.res_bodies import err, log_err, ok
from utils.sessions import verify_requester
from utils.validation import validate_file, vars_fail
import re

class UpdateProfileData(BaseModel):
    name: str
    iconUri: str
    acronym: str
    type: str
    country: str
    website: str

@app.patch('/api/administratives/update-profile')
def update_profile(
    req: Request,
    res: Response,
    data: UpdateProfileData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    uri_validation = None

    if len(data.iconUri) > 0:
        uri_validation = validate_file(
            data.iconUri,
            10 * constants.MEGABYTE,
            'image/(gif|jpeg|png|webp|svg\\+xml)'
        )
    
    if uri_validation and uri_validation[0] == False:
        res.status_code = 400
        return err(uri_validation[1])

    if uri_validation:
        parsed_img_uri = uri_validation[1]
    else:
        parsed_img_uri = {
            'media_type': 'image/gif',
            'content': memoryview(b'')
        }
    
    trimmed_name = data.name.strip()
    trimmed_acronym = data.acronym.strip()
    trimmed_website = data.website.strip()

    if body := vars_fail(
        (
            trimmed_name,
            lambda name: len(name) <= 200,
            partial(err, 'Su nombre es muy largo')
        ),
        (
            trimmed_acronym,
            lambda ac: len(ac) <= 100,
            partial(err, 'Su acrónimo es muy largo')
        ),
        (
            data.type,
            lambda ty: ty in ('publica', 'privada', 'comunitaria'),
            partial(err, 'Tipo no válido')
        ),
        (
            data.country,
            lambda c: c in ('otro', 'mexico', 'china'),
            partial(err, 'País no válido')
        )
    ):
        res.status_code = 400
        return body

    if (
        len(trimmed_website) > 0 and
        not re.match('https?://', trimmed_website, re.I)
    ):
        trimmed_website = 'http://' + trimmed_website

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'update administratives set name = %s, acronym = %s, type = %s, country = %s, website = %s, icon = %s, icon_media_type = %s where id = %s',
                [
                    trimmed_name,
                    trimmed_acronym,
                    data.type,
                    data.country,
                    trimmed_website,
                    parsed_img_uri['content'],
                    parsed_img_uri['media_type'],
                    verif['idRolePair']['id']
                ]
            )
            conn.commit()

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
            