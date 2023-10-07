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
        "proc_name": 'qry_lstbureauex',
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
        "proc_name": 'qry_getbureauex',
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
        "request_mapping_function": add_bureau_exception_list_req_mapping,
        "response_mapping_function": add_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def delete_bureau_exception_list(pk, data, jwt_token):
    '''
    Delete Bureau Exception List
    '''
    args = {
        "pk": pk,
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": delete_bureau_exception_list_req_mapping,
        "response_mapping_function": delete_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def update_bureau_exception_list(pk, data, jwt_token):
    print("UPDATE BUREAU EXCEPTION LIST SERVICE", pk, data)
    '''
    Update Bureau Exception List
    '''
    args = {
        "pk": pk,
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": update_bureau_exception_list_req_mapping,
        "response_mapping_function": update_bureau_exception_list_res_mapping,
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
            
    def bureau_execp_list_map(x):
        return {
            'org_code': x.get('ORG_CODE') or '-',
            'org_short_desc': x.get('ORGS_SHORT_DESC'),
        }

    return list(map(bureau_execp_list_map, data.get('QRY_LSTBUREAUS_REF')))

def bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_pv_id': "",
        'i_emp_hru_id': "",
    }

def bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List failed.")
        return None
        
    def bureau_execp_map(x):
        return {
            'id': x.get('PV_ID') or '-',
            'name': x.get('EMP_FULL_NAME'),
            'bureaus': x.get('BUREAU_NAME_LIST'),
            'seq_num': x.get('SEQ_NUM'),
            'hru_id': x.get('HRU_ID'),
            'sequence_number': x.get('SEQ_NUM'),
            'param_value': x.get('PARM_VALUES'),
        }

    return list(map(bureau_execp_map, data.get('QRY_LSTBUREAUEXCEPTIONS_REF')))


def add_bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PV_ID': request.get('id') or '',
        'EMP_FULL_NAME': request.get('name') or '',
        'BUREAU_NAME_LIST': request.get('bureaus') or [],
        'i_emp_hru_id': '',
        'i_PV_VALUE_TXT': '',
        'I_PPOS_LAST_UPDT_USER_ID': '',
        'I_PPOS_LAST_UPDT_TMSMP_DT': '',
    }

def add_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data

def delete_bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PV_ID': request.get('id') or '',
        'EMP_FULL_NAME': '',
        'BUREAU_NAME_LIST': '',
        'i_emp_hru_id': '',
        'i_PV_VALUE_TXT': '',
        'I_PPOS_LAST_UPDT_USER_ID': '',
        'I_PPOS_LAST_UPDT_TMSMP_DT': '',
    }

def delete_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data

def update_bureau_exception_list_req_mapping(request):
    print("UPDATE BUREAU EXCEPTION LIST SERVICE REQUEST MAPPING", request)
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        '_pv_id': request.get('id') or 0,
        'i_emp_hru_id': request.get('empHruId') or '',
    }

def update_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data