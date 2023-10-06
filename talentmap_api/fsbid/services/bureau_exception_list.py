import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
from django.conf import settings

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

BUREAU_EXCEPTION_LIST_ROOT = settings.BUREAU_EXCEPTION_LIST_API_URL

logger = logging.getLogger(__name__)

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