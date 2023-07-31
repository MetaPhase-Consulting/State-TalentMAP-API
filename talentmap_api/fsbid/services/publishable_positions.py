import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
from django.conf import settings

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

PUBLISHABLE_POSITIONS_ROOT = settings.PUBLISHABLE_POSITIONS_API_URL

logger = logging.getLogger(__name__)


def get_capsule_description(id, jwt_token):
    '''
    Gets an individual capsule description
    '''
    capsule_description = services.send_get_request(
        "capsule",
        {"id": id},
        convert_capsule_query,
        jwt_token,
        fsbid_capsule_to_talentmap_capsule,
        None,
        "/api/v1/fsbid/publishablePositions/",
        None,
        PUBLISHABLE_POSITIONS_ROOT
    )
    return pydash.get(capsule_description, 'results[0]') or None

def update_capsule_description(jwt_token, id, description, last_updated_date, updater_id):
    '''
    Updates capsule description on publishable position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"{PUBLISHABLE_POSITIONS_ROOT}/capsule"
    url = f"{uri}?pos_seq_num={id}&capsule_descr_txt={description}&last_updated_date={last_updated_date}&update_id={updater_id}&ad_id={ad_id}"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response

def fsbid_capsule_to_talentmap_capsule(capsule):
    '''
    Formats FSBid response to Talentmap format
    '''
    return {
        "id": capsule.get("pos_seq_num", None),
        "description": capsule.get("capsule_descr_txt", None),
        "last_updated_date": capsule.get("update_date", None),
        "updater_id": capsule.get("update_id", None),
    }

def convert_capsule_query(query):
    '''
    Converts TalentMap query to FSBid
    '''
    values = {
        "pos_seq_num": query.get("id", None),
        "ad_id": query.get("ad_id", None),
        "update_date": query.get("last_updated_date", None),
        "update_id": query.get("updater_id", None),
        "capsule_descr_txt": query.get("description", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def get_publishable_positions(jwt_token):
    '''
    Gets Publishable positions
    '''
    args = services.send_get_request(
        "",
        {},
        convert_publishable_positions_query,
        jwt_token,
        publishable_positions__fisbid_to_talentmap,
        None,
        "/api/v1/fsbid/publishablePositions/",
        None,
        PUBLISHABLE_POSITIONS_ROOT
    )
    return pydash.get(args, 'results[0]') or None

def edit_publishable_position(jwt_token, id, description, updater_id):
    '''
    Edits Publishable position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"{PUBLISHABLE_POSITIONS_ROOT}/{id}"
    url = f"{uri}?capsule_descr_txt={description}&update_id={updater_id}"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response

def publishable_positions__fisbid_to_talentmap(capsule):
    '''
    Formats FSBid response to TalentMAP format
    '''
    return {
        "id": capsule.get("pos_seq_num", None),
        "description": capsule.get("capsule_descr_txt", None),
        "last_updated_date": capsule.get("update_date", None), # maybe
        "updater_id": capsule.get("update_id", None), # maybe
    }

def convert_publishable_positions_query(query):
    '''
    Converts TalentMap query to FSBid
    '''
    values = {
        "pos_seq_num": query.get("id", None),
        "capsule_descr_txt": query.get("description", None),
        "update_id": query.get("updater_id", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
