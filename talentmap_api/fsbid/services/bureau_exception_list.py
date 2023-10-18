import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
from django.conf import settings

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

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
        "proc_name": 'act_addbureauex',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": add_bureau_exception_list_req_mapping,
        "response_mapping_function": add_bureau_exception_list_res_mapping,
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
        "proc_name": 'act_delbureauex',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": delete_bureau_exception_list_req_mapping,
        "response_mapping_function": delete_bureau_exception_list_res_mapping,
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
        "proc_name": 'act_modbureauex',
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
            'bureauCode': x.get('ORG_CODE') or '-',
            'description': x.get('ORGS_SHORT_DESC'),
        }

    return list(map(bureau_execp_list_map, data.get('QRY_LSTBUREAUS_REF')))

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
            'pv_id': x.get('PV_ID') or '-',
            'name': x.get('EMP_FULL_NAME'),
            'bureaus': x.get('BUREAU_NAME_LIST'),
            'seqNum': x.get('SEQ_NUM'),
            'id': x.get('HRU_ID'),
            'bureauCodes': x.get('i_PV_VALUE_TXT'),
        }

    return list(map(bureau_execp_map, data.get('QRY_LSTBUREAUEXCEPTIONS_REF')))


def add_bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PV_ID': '',
        'i_emp_hru_id': request.get('id') or '',
        'i_PV_VALUE_TXT': request.get('bureauCodes') or '',
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
        'i_PV_ID': request.get('pv_id') or '',
        'i_emp_hru_id': request.get('id') or '',
        'i_PV_VALUE_TXT': '',
    }

def delete_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data

def update_bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        '_pv_id': request.get('pv_id') or 0,
        'i_emp_hru_id': request.get('id') or '',
        "i_PV_VALUE_TXT": request.get('bureauCodes') or '',
        "i_last_update_date": "",
        "i_last_update_id": "",
    }

def update_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data