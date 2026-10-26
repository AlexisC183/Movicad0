from fastapi import Request, Response
from app import app
from pydantic import BaseModel
from utils import constants
from utils.res_bodies import err
from utils.sessions import verify_requester
from utils.validation import validate_file

class UpdateProfileData(BaseModel):
    name: str
    iconUri: str

"""
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
    
    if uri_validation and not uri_validation[0]:
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
"""