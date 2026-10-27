from fastapi import Request, Response
from app import app
from db import dbconn
from pydantic import BaseModel
from utils import constants
from utils.res_bodies import err, no_account, log_err, ok
from utils.sessions import verify_requester
from utils.validation import validate_file

class UpdateProfileData(BaseModel):
    name: str
    iconUri: str

@app.patch('/api/students/update-profile')
def update_profile(
    req: Request,
    res: Response,
    data: UpdateProfileData
):
    verif = verify_requester(req, constants.STUDENT)
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

    if len(trimmed_name) > 100:
        res.status_code = 400
        return err('Su nombre es muy largo')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select exists (select 1 from users where not deleted and id = %s)',
                [verif['idRolePair']['id']]
            )
            if not c.fetchone()[0]:
                res.status_code = 401
                return no_account()
            
            c.execute(
                'update students set name = %s, icon = %s, icon_media_type = %s where id = %s',
                [
                    trimmed_name,
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
            