from fastapi import Request, Response, Query
from app import app
from db import dbconn
from pydantic import BaseModel
from functools import partial
from utils import constants
from utils import sql
from utils.converters import try_int
from utils.res_bodies import err, log_err, ok, not_found
from utils.sessions import verify_requester
from utils.validation import validate_file, vars_fail
from typing import Annotated
import base64
import re

@app.get('/api/administratives/read')
def read_all(
    req: Request,
    res: Response,
    cursor_pos_maybe: Annotated[int | None, Query(alias='cursor-pos')] = None,
    search_term: Annotated[str, Query(alias='search-term')] = '',
    type: str = '',
    country: str = ''
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    trimmed_search_term = search_term.strip()

    json_keys = ['id', 'name', 'type', 'country', 'icon', 'iconMediaType']
    query = 'select a.id, a.name, a.type, a.country, a.icon, a.icon_media_type from administratives a join users u on a.id = u.id'
    where = 'where not u.deleted'

    param_vals = []
    if trimmed_search_term:
        where += ' and (a.name like %s or a.acronym like %s or a.id = %s)'
        param_vals = [
            f'%{ trimmed_search_term }%',
            f'%{ trimmed_search_term }%',
            try_int(trimmed_search_term)
        ]
    elif type:
        where += ' and a.type = %s'
        param_vals = [type]
    elif country:
        where += ' and a.country = %s'
        param_vals = [country]

    conn = None
    try:
        conn = dbconn()
        if cursor_pos_maybe is None:
            cursor_pos = sql.get_init_cursor_pos(
                conn,
                f'select a.id from administratives a join users u on a.id = u.id { where }',
                'a.id',
                param_vals
            )
        else:
            cursor_pos = cursor_pos_maybe

        admin_rows = sql.fetch_paginated(
            conn,
            f'{ query } { where }',
            'a.id',
            param_vals,
            cursor_pos
        )
        admins = [dict(zip(json_keys, row)) for row in admin_rows]

        for admin in admins:
            admin['icon'] = base64.b64encode(admin['icon'].tobytes())

        if len(admins) == constants.PAGE_SIZE:
            new_cursor_pos = admins[-1]['id']
        else:
            new_cursor_pos = constants.FINAL_CURSOR_POS
      
        res.status_code = 200
        return ok({
            'cursorPosition': new_cursor_pos,
            'administratives': admins
        }) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

@app.get('/api/administratives/read/{id}')
def read(
    req: Request,
    res: Response,
    id: int
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    json_keys = [
        'id',
        'acronym',
        'icon',
        'iconMediaType',
        'name',
        'type',
        'country',
        'website'
    ]
    query = 'select a.id, a.acronym, a.icon, a.icon_media_type, a.name, a.type, a.country, a.website from administratives a join users u on a.id = u.id where not u.deleted and u.id = %s'
    conn = None

    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(query, [id])
            admin_row = c.fetchone()

            if not admin_row:
                res.status_code = 404
                return not_found()

            admin = dict(zip(json_keys, admin_row))

            res.status_code = 200
            return ok(admin) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

@app.get('/api/administratives/me')
def dashboard(req: Request, res: Response):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    open_cf_cnt_q = "select count(*) from calls_for where not deleted and administrative_id = %s and now() between coalesce(initial_date, '-infinity') and coalesce(final_date, 'infinity')"

    cf_cnt_q = 'select count(*) from calls_for where not deleted and administrative_id = %s'

    cf_history_cnt_q = 'select count(*) from calls_for where administrative_id = %s'

    applicant_cnt_q = """
    select count(ap.*)
    from applications ap
    join calls_for cf on ap.call_for_id = cf.id
    join users s on ap.student_id = s.id
    where not s.deleted and not ap.deleted and not cf.deleted and cf.administrative_id = %s
    """

    applicant_avg_q = """
    select avg(appl_cnt) from (
        select cf.id as call_for, count(ap.*) as appl_cnt
        from calls_for cf
        left join applications ap on cf.id = ap.call_for_id
        join users s on ap.student_id = s.id
        where not s.deleted and not ap.deleted and not cf.deleted and cf.administrative_id = %s
        group by cf.id
    )
    """
    
    gt1_cf_applicant_cnt_q = """
    select count(*) from (
        select student, count(call_for) from (
            select cf.id as call_for, ap.student_id as student
            from calls_for cf
            join applications ap on cf.id = ap.call_for_id
            join users s on ap.student_id = s.id
            where not s.deleted and not ap.deleted and not cf.deleted and cf.administrative_id = %s
        )
        group by student having count(call_for) > 1
    )
    """

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                f'select ({ open_cf_cnt_q }), ({ cf_cnt_q }), ({ cf_history_cnt_q }), ({ applicant_cnt_q }), ({ applicant_avg_q }), ({ gt1_cf_applicant_cnt_q })',
                [verif['idRolePair']['id']] * 6
            )

            json_keys = [
                'openCallsFor',
                'activeCallsFor',
                'callForHistory',
                'applicants',
                'applicantAverage',
                'moreThanOneCallForApplicantCount'
            ]
            stats = dict(zip(json_keys, c.fetchone()))

            res.status_code = 200
            return ok(stats) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

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
            