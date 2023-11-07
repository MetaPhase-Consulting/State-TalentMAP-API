import logging
from urllib.parse import urlencode, quote

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

def get_bureau_exception_list(query, jwt_token):
    '''
    Gets Bureau Exception List of Users
    '''
    args = {
        "proc_name": 'qry_lstbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": bureau_exception_list_req_mapping,
        "response_mapping_function": bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

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
            'pvId': x.get('PV_ID'),
            'name': x.get('EMP_FULL_NAME'),
            'bureaus': x.get('BUREAU_NAME_LIST') if x.get('BUREAU_NAME_LIST') != " " else None,
            'seqNum': x.get('EMP_SEQ_NBR'),
            'id': x.get('HRU_ID'),
            'bureauCodeList': x.get('PARM_VALUES') if x.get('PARM_VALUES') != " " else None,
        }

    return list(map(bureau_execp_map, data.get('QRY_LSTBUREAUEXCEPTIONS_REF')))


def get_users_bureau_list(query, jwt_token):
    '''
    Gets Bureau Exception List of Bureaus
    '''
    args = {
        "proc_name": 'qry_getbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": bureau_exception_list_of_bureaus_req_mapping,
        "response_mapping_function": bureau_exception_list_of_bureaus_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def bureau_exception_list_of_bureaus_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pv_id'),
        'i_emp_hru_id': request.get('id'),
    }

def bureau_exception_list_of_bureaus_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for User Bureau List failed.")
        return None
            
    def bureau_execp_list_map(x):
        return {
            'bureauCode': x.get('ORG_CODE'),
            'description': x.get('ORGS_SHORT_DESC'),
        }
    bureau_exceptions_info = {
        "id": data.get('O_EMP_HRU_ID'),
        "name": data.get('O_EMP_FULL_NAME'),
        "pvId": data.get('O_PV_ID'),
        "user_code_list": data.get('O_PV_VALUE_TXT'),
        "lastUpdated": data.get('O_LAST_UPDATE_DATE'),
        "lastUpdatedUserID": data.get('O_LAST_UPDATE_ID'),
        "bureauRefList" : list(map(bureau_execp_list_map, data.get('QRY_LSTBUREAUS_REF'))),
    }
    return bureau_exceptions_info

def add_bureau_exception_list(data, jwt_token):
    '''
    Adds Bureau from users Bureau Access List
    '''
    args = {
        "proc_name": 'act_addbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": add_bureau_exception_list_req_mapping,
        "response_mapping_function": add_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def add_bureau_exception_list_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': '',
        'i_emp_hru_id': request.get('id'),
        'i_PV_VALUE_TXT': request.get('bureauCodeList'),
    }

def add_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data


def delete_bureau_exception_list(data, jwt_token):
    '''
    Removes Bureau from users Bureau Access List
    '''
    args = {
        "proc_name": 'act_delbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": delete_bureau_exception_list_req_mapping,
        "response_mapping_function": delete_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def delete_bureau_exception_list_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pv_id'),
        'i_emp_hru_id': request.get('id'),
        'i_last_update_id': request.get('lastUpdatedUserID'),
        'i_last_update_date': request.get('lastUpdated'),
    }

def delete_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data



def update_bureau_exception_list(data, jwt_token):
    '''
    Updates Bureau from users Bureau Access List
    '''
    args = {
        "proc_name": 'act_modbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": update_bureau_exception_list_req_mapping,
        "response_mapping_function": update_bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def update_bureau_exception_list_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pv_id'),
        'i_emp_hru_id': request.get('id'),
        "i_PV_VALUE_TXT": request.get('bureauCodeList'),
        'i_last_update_id': request.get('lastUpdatedUserID'),
        'i_last_update_date': request.get('lastUpdated'),
    }

def update_bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List Edit failed.")
        return None

    return data
