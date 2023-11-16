import logging
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

def get_bureau_exceptions(query, jwt_token):
    '''
    Get Bureau Exceptions
    '''
    args = {
        "proc_name": 'qry_lstbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": bureau_exceptions_req_mapping,
        "response_mapping_function": bureau_exceptions_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
def bureau_exceptions_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }
def bureau_exceptions_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for Bureau Exceptions failed.")
        return None
        
    def bureau_execp_map(x):
        return {
            'pvId': x.get('PV_ID'),
            'name': x.get('EMP_FULL_NAME'),
            'bureaus': x.get('BUREAU_NAME_LIST') if x.get('BUREAU_NAME_LIST') != " " and x.get('BUREAU_NAME_LIST') != "" else None,
            'seqNum': x.get('EMP_SEQ_NBR'),
            'id': x.get('HRU_ID'),
            'bureauCodeList': x.get('PARM_VALUES') if x.get('PARM_VALUES') != " " else None,
        }

    return list(map(bureau_execp_map, data.get('QRY_LSTBUREAUEXCEPTIONS_REF')))


def get_bureau_exceptions_ref_data_bureaus(query, jwt_token):
    '''
    Get Bureau Exceptions Ref Data for Bureaus
    '''
    args = {
        "proc_name": 'qry_addbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": bureau_exceptions_ref_data_bureaus_req_mapping,
        "response_mapping_function": bureau_exceptions_ref_data_bureaus_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
def bureau_exceptions_ref_data_bureaus_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }
def bureau_exceptions_ref_data_bureaus_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for Bureau Exceptions Ref Data for Bureaus failed.")
        return None

    def bureau_execp_ref_data_map(x):
        return {
            'code': x.get('ORG_CODE'),
            'short_description': x.get('ORGS_SHORT_DESC'),
            'long_description': x.get('ORGS_LONG_DESC'),
        }

    return list(map(bureau_execp_ref_data_map, data.get('QRY_LSTBUREAUS_REF')))


def get_user_bureau_exceptions_and_metadata(data, jwt_token):
    '''
    Get User Bureau Exceptions and MetaData Required for Actions
    '''
    args = {
        "proc_name": 'qry_getbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": user_bureau_exceptions_and_metadata_req_mapping,
        "response_mapping_function": user_bureau_exceptions_and_metadata_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )
def user_bureau_exceptions_and_metadata_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pvId'),
        'i_emp_hru_id': request.get('id'),
    }
def user_bureau_exceptions_and_metadata_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for User Bureau Exceptions and MetaData Required for Actions failed.")
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
        "userCodeList": data.get('O_PV_VALUE_TXT'),
        "lastUpdated": data.get('O_LAST_UPDATE_DATE'),
        "lastUpdatedUserID": data.get('O_LAST_UPDATE_ID'),
        "bureauRefList" : list(map(bureau_execp_list_map, data.get('QRY_LSTBUREAUS_REF'))),
    }
    return bureau_exceptions_info


def add_user_bureau_exceptions(data, jwt_token):
    '''
    Add Bureau Exceptions to a User
    used the first time Bureau Exceptions are added to a user
    '''
    args = {
        "proc_name": 'act_addbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": add_user_bureau_exceptions_req_mapping,
        "response_mapping_function": add_user_bureau_exceptions_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )
def add_user_bureau_exceptions_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': '',
        'i_emp_hru_id': request.get('id'),
        'i_PV_VALUE_TXT': request.get('bureauCodeList'),
    }
def add_user_bureau_exceptions_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for Adding Bureau Exceptions to a User failed.")
        return None

    return data


def update_user_bureau_exceptions(data, jwt_token):
    '''
    Update User Bureau Exceptions
    '''
    args = {
        "proc_name": 'act_modbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": update_user_bureau_exceptions_req_mapping,
        "response_mapping_function": update_user_bureau_exceptions_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )
def update_user_bureau_exceptions_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pvId'),
        'i_emp_hru_id': request.get('id'),
        "i_PV_VALUE_TXT": request.get('bureauCodeList'),
        'i_last_update_id': request.get('lastUpdatedUserID'),
        'i_last_update_date': request.get('lastUpdated'),
    }
def update_user_bureau_exceptions_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for Updating User Bureau Exceptions failed.")
        return None

    return data


def delete_user_bureau_exceptions(data, jwt_token):
    '''
    Deletes all Bureau Exceptions from a User
    will remove all Bureau Exceptions from User, regardless of it all Bureaus are sent in for removal
    '''
    args = {
        "proc_name": 'act_delbureauex',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": delete_user_bureau_exceptions_req_mapping,
        "response_mapping_function": delete_user_bureau_exceptions_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )
def delete_user_bureau_exceptions_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'PV_AD_ID_I': '',
        'i_pv_id': request.get('pvId'),
        'i_emp_hru_id': request.get('id'),
        'i_last_update_id': request.get('lastUpdatedUserID'),
        'i_last_update_date': request.get('lastUpdated'),
    }
def delete_user_bureau_exceptions_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"FSBid call for Deleting all Bureau Exceptions from a User failed.")
        return None

    return data




