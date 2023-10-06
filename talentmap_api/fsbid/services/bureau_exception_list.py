import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
from django.conf import settings

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

BUREAU_EXCEPTION_LIST_ROOT = settings.BUREAU_EXCEPTION_LIST_API_URL

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
        "/api/v1/fsbid/bureauExceptionList/",
        None,
        BUREAU_EXCEPTION_LIST_ROOT
    )
    return pydash.get(capsule_description, 'results[0]') or None

def update_capsule_description(jwt_token, id, description, last_updated_date, updater_id):
    '''
    Updates capsule description on bureau exception list
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"{BUREAU_EXCEPTION_LIST_ROOT}/capsule"
    url = f"{uri}?pos_seq_num={id}&capsule_descr_txt={description}&update_id={last_updated_date}&update_id={updater_id}&ad_id={ad_id}"
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

def get_bureau_exception_list(query, jwt_token):
    '''
    Gets Bureau Exception List
    '''
    args = {
        "proc_name": 'qry_modPublishPos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": bureau_exception_list_req_mapping,
        "response_mapping_function": bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def get_bureau_exception_list_of_bureaus(query, jwt_token):
    '''
    Gets Bureau Exception List of Bureaus
    '''
    args = {
        "proc_name": 'qry_modPublishPos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": bureau_exception_list_of_bureaus_req_mapping,
        "response_mapping_function": bureau_exception_list_of_bureaus_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
def add_bureau_exception_list(data, jwt_token):
    '''
    Add Bureau Exception List
    '''
    args = {
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": edit_bureau_exception_list_req_mapping,
        "response_mapping_function": edit_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def delete_bureau_exception_list(data, jwt_token):
    '''
    Delete Bureau Exception List
    '''
    args = {
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": edit_bureau_exception_list_req_mapping,
        "response_mapping_function": edit_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def update_bureau_exception_list(data, jwt_token):
    '''
    Update Bureau Exception List
    '''
    args = {
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": save_bureau_exception_list_req_mapping,
        "response_mapping_function": save_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def bureau_exception_list_of_bureaus_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_pv_id': "",
        'i_emp_hru_id': "",
    }

def bureau_exception_list_of_bureaus_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List failed.")
        return None

def bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List failed.")
        return None

    def bureau_execp_map(x):
        return {
            'id': x.get('JC_ID') or '-',
            'name': x.get('POS_NUM_TXT'),
            'bureaus': x.get('BUR_SHORT_DESC'),
        }

    return list(map(bureau_execp_map, data.get('QRY_MODPUBLISHPOS_REF')))


    def edit_bureau_exception_list_req_mapping(request):
        return {
            'PV_API_VERSION_I': '',
            'PV_AD_ID_I': '',
            '_pv_id': request.get('id') or 0,
            'i_emp_hru_id': request.get('empHruId') or '',
        }

    def edit_bureau_exception_list_res_mapping(data):
        if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
            logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
            return None

        return data

    def save_bureau_exception_list_req_mapping(request):
        return {
            'PV_API_VERSION_I': '',
            'PV_AD_ID_I': '',
            '_pv_id': request.get('id') or 0,
            'i_emp_hru_id': request.get('empHruId') or '',
        }

    def save_bureau_exception_list_res_mapping(data):
        if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
            logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
            return None

        return data