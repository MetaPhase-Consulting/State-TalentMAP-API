import logging

import pydash

from django.conf import settings

from talentmap_api.fsbid.services import common as services

FAVORITES_LIMIT = settings.FAVORITES_LIMIT
PV_API_V2_URL = settings.PV_API_V2_URL

API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)

# ======================== Panel Remark ========================

def submit_create_remark(remark, jwt_token={}):
    url = f"{API_ROOT}/v1/admin_panels/"

    remark['mutuallyExclusive'] = "N"

    args = {
        "uri": url,
        "query": remark,
        "query_mapping_function": convert_panel_admin_remark_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )

def convert_panel_admin_remark_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    return {
        "TBD_WS_rmrkInsertionList":  pydash.get(query, 'rmrkInsertionList'),
        "TBD_WS_longDescription": pydash.get(query, 'longDescription'),
        "TBD_WS_activeIndicator": pydash.get(query, 'activeIndicator'),
        "TBD_WS_mutuallyExclusive": pydash.get(query, 'mutuallyExclusive') or "N",
    }

# ======================== Panel Meeting ========================

def get_panel_meeting(pk, jwt_token):
    '''
    Gets Panel Meeting
    '''
    args = {
        "proc_name": "qry_getPnlMeet",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT99",
        "request_body": pk,
        "request_mapping_function": panel_meeting_request_mapping,
        "response_mapping_function": panel_meeting_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def panel_meeting_request_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_PM_SEQ_NUM": request,
    }

def panel_meeting_response_mapping(response):
    def dates(x):
        return {
            'code': x.get('MDT_CODE'),
            'description': x.get('MDT_DESC_TEXT'),
            'date': x.get('PMD_DTTM'),
        }
    return {
        'panel_id': response.get('O_PM_SEQ_NUM'),
        'type_code': response.get('O_PMT_CODE'),
        'type_description': response.get('O_PMT_DESC_TEXT'),
        'status_code': response.get('O_PMS_CODE'),
        'status_description': response.get('O_PMS_DESC_TEXT'),
        'panel_dates': list(map(dates, response.get('QRY_LSTPMD_REF'))),
    }

# ======================== Edit Panel Meeting ========================

def edit_panel_meeting(data, jwt_token):
    '''
    Edit Panel Meeting
    '''
    args = {
        "proc_name": 'act_modPnlMeet',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": edit_panel_meeting_req_mapping,
        "response_mapping_function": edit_panel_meeting_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_panel_meeting_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_PMT_CODE": "",
        "I_PMS_CODE ": "",
        "I_PM_DELETE_IND": "",
        "I_PM_SEQ_NUM": "",
        "I_PM_VIRTUAL_IND": "",
        "I_PM_UPDATE_ID": "",
        "I_PM_UPDATE_DATE": "",
        "I_INC_IND": "",
        "I_PMD_DTTM": "",
        "I_MDT_CODE": "",
        "I_PMD_UPDATE_ID": "",
        "I_PMD_UPDATE_DATE": ""
    }

def edit_panel_meeting_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Panel Meeting Edit failed.")
        return None

    return data

# ======================== Post Panel Processing ========================

def get_post_panel(pk, jwt_token):
    '''
    Gets Post Panel Processing
    '''
    args = {
        "proc_name": "qry_modPostPnl",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT99",
        "request_body": pk,
        "request_mapping_function": post_panel_request_mapping,
        "response_mapping_function": post_panel_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def post_panel_request_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_PM_SEQ_NUM": request,
    }

def post_panel_response_mapping(response):
    def statuses(x):
        return {
            'code': x.get('AIS_CODE'),
            'description': x.get('AIS_ABBR_DESC_TEXT'),
            'short_description': x.get('AIS_DESC_TEXT'),
        }
    def values(x):
        return {
            'valid': x.get('AI_VALID_IND'),
            'item': x.get('PMI_OFFICIAL_ITEM_NUM'),
            'label': x.get('AI_LABEL_TEXT'),
            'employee': x.get('EMP_FULL_NAME'),
            'status': x.get('AIS_ABBR_DESC_TEXT'),
            'sequence_number': x.get('AI_SEQ_NUM'),
            'update_id': x.get('AI_UPDATE_ID'),
            'update_date': x.get('AI_UPDATE_DATE'),
            'aht_code': x.get('AHT_CODE'),
            'aih_hold_number': x.get('AIH_HOLD_NUM'),
            'aih_hold_comment': x.get('AIH_HOLD_COMMENT_TEXT'),
            'aih_sequence_number': x.get('AIH_SEQ_NUM'),
        }
    return {
        'statuses': list(map(statuses, response.get('QRY_LSTAIS_DD_REF'))),
        'values': list(map(values, response.get('QRY_MODPOSTPNL_REF'))),
    }

# ======================== Edit Post Panel Processing ========================

def edit_post_panel(data, jwt_token):
    '''
    Edit Post Panel Processing
    '''
    args = {
        "proc_name": 'act_modPostPnl',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": edit_post_panel_req_mapping,
        "response_mapping_function": edit_post_panel_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_post_panel_req_mapping(request):
    ais_code = request.get('status')
    if ais_code == 'H':
        return {
            "pv_api_version_i": "",
            "PV_AD_ID_I": "",
            "I_AI_SEQ_NUM": request.get('sequence_number'),
            "I_AI_UPDATE_ID": request.get('update_id'),
            "I_AI_UPDATE_DATE": request.get('update_date'),
            "I_AI_AIS_CODE": ais_code,
            "I_AHT_CODE": request.get('aht_code'),
            "I_AIH_HOLD_COMMENT_TEXT": request.get('aih_hold_comment'),
            "I_AIH_HOLD_NUM": request.get('aih_hold_number'),
            "I_AIH_SEQ_NUM": request.get('aih_sequence_number'),
            "I_AIH_UPDATE_ID": "",
            "I_AIH_UPDATE_DATE": ""
        }
    return {
        "pv_api_version_i": "",
        "PV_AD_ID_I": "",
        "I_AI_SEQ_NUM": request.get('sequence_number'),
        "I_AI_UPDATE_ID": request.get('update_id'),
        "I_AI_UPDATE_DATE": request.get('update_date'),
        "I_AI_AIS_CODE": ais_code
    }

def edit_post_panel_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Post Panel Processing Edit failed.")
        return None

    return data

# ======================== Panel Run Actions ========================

def run_preliminary(data, jwt_token):
    '''
    Run Official Preliminary
    '''
    args = {
        "proc_name": 'act_runoffpre',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": run_panel_req_mapping,
        "response_mapping_function": run_preliminary_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def run_panel_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_PM_SEQ_NUM": request,
    }

def run_preliminary_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Run Official Preliminary failed.")
        return None

    return data

def run_addendum(data, jwt_token):
    '''
    Run Official Addendum
    '''
    args = {
        "proc_name": 'act_runoffaddendum',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": run_panel_req_mapping,
        "response_mapping_function": run_addendum_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def run_addendum_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Run Official Addendum failed.")
        return None

    return data

def run_post_panel(data, jwt_token):
    '''
    Run Post Panel
    '''
    args = {
        "proc_name": 'act_runpostpnl',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": run_panel_req_mapping,
        "response_mapping_function": run_post_panel_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def run_post_panel_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Run Post Panel failed.")
        return None

    return data
