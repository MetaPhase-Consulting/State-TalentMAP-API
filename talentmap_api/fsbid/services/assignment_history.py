import logging
from functools import partial
import jwt
from urllib.parse import urlencode, quote
from django.conf import settings

import pydash

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.fsbid.services import common as services

API_ROOT = settings.WS_ROOT_API_URL


logger = logging.getLogger(__name__)


# ======== Get Assignment History ========

def get_assignments(query, jwt_token):
    '''
    Get assignments
    '''
    response = services.send_get_request(
        "v2/assignments/",
        query,
        convert_assignments_query,
        jwt_token,
        fsbid_assignments_to_talentmap_assignments,
        None,
        "/api/v2/assignments/",
        None,
        API_ROOT,
    )
    return response

def assignment_history_to_client_format(data):
    # needs to be updated once fully integrated
    from talentmap_api.fsbid.services.common import get_post_overview_url, get_post_bidding_considerations_url, get_obc_id
    assignmentsCopy = []
    tmap_assignments = []
    if type(data['results']) is type(dict()):
        assignmentsCopy.append(data['results'])
    else:
        assignmentsCopy = data['results']
    if type(assignmentsCopy) is type([]):
        for x in assignmentsCopy:
            pos = pydash.get(x, 'position[0]') or {}
            loc = pydash.get(pos, 'location[0]') or {}
            tmap_assignments.append(
                {
                    "id": x['id'],
                    "position_id": x['position_id'],
                    "start_date": ensure_date(x['start_date']),
                    "end_date": ensure_date(x['end_date']),
                    # TO DO: Clean up
                    "status": x['asgd_asgs_text'] or x['asgd_asgs_code'],
                    "tod_code": x.get('tod_code') or None,
                    "tod_desc_text": x.get('tod_desc_text') or None,
                    "tod_short_desc": x.get('tod_short_desc') or None,
                    "asgd_tod_other_text": x.get('asgd_tod_other_text') or None,
                    "asgd_revision_num": x['asgd_revision_num'],
                    "position": {
                        "grade": pos.get("posgradecode") or None,
                        "skill": f"{pos.get('posskilldesc') or None} ({pos.get('posskillcode')})",
                        "skill_code": pos.get("posskillcode") or None,
                        "bureau": f"({pos.get('pos_bureau_short_desc') or None}) {pos.get('pos_bureau_long_desc') or None}",
                        "bureau_code": pydash.get(pos, 'bureau.bureau_short_desc'), # only comes through for available bidders
                        "organization": pos.get('posorgshortdesc') or None,
                        "position_number": pos.get('posnumtext') or None,
                        "position_id": x['position_id'],
                        "title": pos.get("postitledesc") or None,
                        "post": {
                            "code": loc.get("locgvtgeoloccd") or None,
                            "post_overview_url": get_post_overview_url(loc.get("locgvtgeoloccd")),
                            "post_bidding_considerations_url": get_post_bidding_considerations_url(loc.get("locgvtgeoloccd")),
                            "obc_id": get_obc_id(loc.get("locgvtgeoloccd")),
                            "location": {
                                "country": loc.get("loccountry") or None,
                                "code": loc.get("locgvtgeoloccd") or None,
                                "city": loc.get("loccity") or None,
                                "state": loc.get("locstate") or None,
                            }
                        },
                        "language": pos.get("pos_position_lang_prof_desc", None),
                        "languages": services.parseLanguagesToArr(pos),
                    },
                    "pos": {
                        **pos,
                        "languages": services.parseLanguagesToArr(pos),
                    },
                }
            )
    return tmap_assignments

def convert_assignments_query(query):
    filters = services.convert_to_fsbid_ql([
        {"col": "asgperdetseqnum", "val": query.get('perdet_seq_num') or None},
        {"col": "asgdrevisionnum", "val": "MAX"},
        {"col": "asgdasgscode", "val": "EF" if query.get('is_effective') else None},
    ])

    values = {
        "rp.pageNum": int(query.get('page', 1)),
        "rp.pageRows": int(query.get('limit', 1000)),
        "rp.filter": filters,
        "rp.columns": "asgperdetseqnum",
        "rp.orderBy": services.sorting_values(query.get("ordering", "-assignment_start_date")),
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_assignments_to_talentmap_assignments(data):
    return {
        "id": data.get("asgdasgseqnum"),
        "asg_emp_seq_nbr": data.get("asgempseqnbr"),
        "asg_perdet_seq_num": data.get("asgperdetseqnum"),
        "position_id": data.get("asgposseqnum"),
        "asg_create_id": data.get("asgcreateid"),
        "asg_create_date": data.get("asgcreatedate"),
        "asg_update_id": data.get("asgupdateid"),
        "asg_update_date": data.get("asgupdatedate"),
        "asgd_asg_seq_num": data.get("asgdasgseqnum"),
        "asgd_revision_num": data.get("asgdrevisionnum"),
        "asgd_asgs_text": data.get("asgsdesctext"),
        "asgd_asgs_code": data.get("asgdasgscode"),
        "asgd_lat_code": data.get("asgdlatcode"),
        "asgd_tfcd": data.get("asgdtfcd"),
        "asgd_tod_code": data.get("asgdtodcode"),
        "asgd_ail_seq_num": data.get("asgdailseqnum"),
        "asgd_org_code": data.get("asgdorgcode"),
        "asgd_wrt_code_rrrepay": data.get("asgdwrtcoderrrepay"),
        "start_date": data.get("asgdetadate"),
        "asgd_adjust_months_num": data.get("asgdadjustmonthsnum"),
        "end_date": data.get("asgdetdteddate"),
        "asgd_salary_reimburse_ind": data.get("asgdsalaryreimburseind"),
        "asgd_travelreimburse_ind": data.get("asgdtravelreimburseind"),
        "asgd_training_ind": data.get("asgdtrainingind"),
        "asgd_create_id": data.get("asgdcreateid"),
        "asgd_create_date": data.get("asgdcreatedate"),
        "asgd_update_id": data.get("asgdupdateid"),
        "asgd_update_date": data.get("asgdupdatedate"),
        "asgd_note_comment_text": data.get("asgdnotecommenttext"),
        "asgd_priority_ind": data.get("asgdpriorityind"),
        "asgd_critical_need_ind": data.get("asgdcriticalneedind"),
        "asgs_code": data.get("asgscode"),
        "asgs_desc_text": data.get("asgsdesctext"),
        "asgs_create_id": data.get("asgscreateid"),
        "asgs_create_date": data.get("asgscreatedate"),
        "asgs_update_id": data.get("asgsupdateid"),
        "asgs_update_date": data.get("asgsupdatedate"),
        # TO DO: reuse position mapping
        "position": data.get("position"),
        "asgd_tod_other_text": data.get("asgdtodothertext"),
        "asgd_tod_months_num": data.get("asgdtodmonthsnum"),
        "tod_code": data.get("todcode"),
        "tod_desc_text": data.get("toddesctext"),
        "tod_months_num": data.get("todmonthsnum"),
        "tod_short_desc": data.get("todshortdesc"),
        "tod_status_code": data.get("todstatuscode"),
    }


# ======== Get Assignments and Separations List ========

def get_assignments_separations(id, jwt_token):
    '''
    Get assignments and separations by perdet from fsbid proc 
    '''
    args = {
        "proc_name": 'qry_lstAsgsSeps',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": get_assignments_separations_req_mapping,
        "response_mapping_function": get_assignments_separations_res_mapping,
        "jwt_token": jwt_token,
        "request_body": { "perdet_seq_num": id },
    }
    return services.send_post_back_office(
        **args
    )

def get_assignments_separations_req_mapping(request):
    return {
        "i_perdet_seq_num": request.get("perdet_seq_num"),
        "pv_api_version_i": "",
        "pv_ad_id_i": "",
    }

def get_assignments_separations_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for fetching assignments and separations failed.')
        return None
    return data


# ======== Get Assignment/Separation Detail and Reference Data ========

def get_assignment_separation(data, jwt_token, is_separation):
    '''
    Get Assignment or Separation Detail and Reference Data
    '''
    if (is_separation):
        args = {
            "proc_name": 'qry_getSepDtl',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": get_separation_req_mapping,
            "response_mapping_function": get_assignment_separation_res_mapping,
            "jwt_token": jwt_token,
            "request_body": data,
        }
    else:
        args = {
            "proc_name": 'qry_getAsgDtl',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": get_assignment_req_mapping,
            "response_mapping_function": get_assignment_separation_res_mapping,
            "jwt_token": jwt_token,
            "request_body": data,
        }
    return services.send_post_back_office(
        **args
    )

def get_assignment_req_mapping(request):
    return {
        "i_asg_seq_num": None if request.get("ignore_params") else request.get("asg_id"),
        "i_asgd_revision_num": None if request.get("ignore_params") else  request.get("revision_num"),
        "pv_api_version_i": "",
        "pv_ad_id_i": "",
    }

def get_separation_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_SEP_SEQ_NUM": None if request.get("ignore_params") else request.get("sep_id"),
        "I_SEPD_REVISION_NUM": None if request.get("ignore_params") else request.get("revision_num"),
        "O_SECREF_ROLE_IND": "",
        "QRY_LSTASGS_REF": "",
        "QRY_LSTLAT_REF": "",
        "QRY_LSTTF_REF": "",
        "QRY_LSTWRT_REF": "",
        "QRY_LSTDIST_REF": "",
        "QRY_LSTNOTP_REF": "",
        "QRY_GETSEPDTL_REF": "",
        "O_RETURN_CODE": "",
        "QRY_ACTION_DATA": "",
        "QRY_ERROR_DATA": ""
    }

def get_assignment_separation_res_mapping(data):
    # if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
    #    logger.error('FSBid call for fetching assignment reference data failed.')
    #    return None
    
    # Skip error handling because there is reference data returned with id based data
    # Scenario 1: fetch id data and ref asg_ref_data_res_mapping (edit existing asg)
    # Scenario 2: fetch just ref data and id data errors (create new asg)
    return data


# ======== Update Assignment/Separation ========

def base_assignment_action_req(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_ASGD_ETA_DATE": request.get("eta"),
        "I_ASGD_ETD_TED_DATE": request.get("etd"),
        "I_ASGD_TOD_CODE": request.get("tod"),
        # TO DO: Clarify custom tod feature
        "I_ASGD_TOD_MONTHS_NUM": request.get("tod_months_num"), 
        "I_ASGD_TOD_OTHER_TEXT": request.get("tod_other_text"), 
        "I_ASGD_ADJUST_MONTHS_NUM": request.get("tod_adjust_months_num"), 
        "I_ASGD_SALARY_REIMBURSE_IND": "Y" if request.get("salary_reimburse_ind") else "N",
        "I_ASGD_TRAVEL_REIMBURSE_IND": "Y" if request.get("travel_reimburse_ind") else "N",
        "I_ASGD_TRAINING_IND": "Y" if request.get("training_ind") else "N",
        "I_ASGD_ORG_CODE": request.get("org_code"),
        "I_ASGD_ASGS_CODE": request.get("status_code"),
        "I_ASGD_LAT_CODE": request.get("lat_code"),
        "I_ASGD_TF_CD": request.get("travel_code"),
        "I_ASGD_WRT_CODE_RR_REPAY": "Y" if request.get("rr_repay_ind") else "N",
        "I_ASGD_NOTE_COMMENT_TEXT": "", # No comment feature
    }

def base_separation_action_req(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_DSC_CD": request.get("location_code"),
        "I_SEPD_SEPARATION_DATE": request.get("separation_date"), 
        "I_SEPD_CITY_TEXT": request.get("city_text"),
        "I_SEPD_COUNTRY_STATE_TEXT": request.get("country_state_text"),
        "I_SEPD_US_IND": request.get("us_ind"),
        "I_ASGS_CODE": request.get("status_code"),
        "I_LAT_CODE": request.get("lat_code"), # Should separation always be "Separation" M LAT?
        "I_TF_CD": request.get("travel_code"),
        "I_WRT_CODE_RR_REPAY": request.get("rr_repay_ind"),
        "I_SEPD_NOTE_COMMMENT_TEXT": "", # No comment feature
    }

def update_assignment_separation(query, jwt_token, is_separation):
    '''
    Update Assignment or Separation
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    if is_separation:
        args = {
            "proc_name": 'act_modSepDtl',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": partial(update_separation_req_mapping, hru_id=hru_id),
            "response_mapping_function": update_separation_res_mapping,
            "jwt_token": jwt_token,
            "request_body": query,
        }
    else:
        args = {
            "proc_name": 'act_modasgdtl',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": partial(update_assignment_req_mapping, hru_id=hru_id),
            "response_mapping_function": update_assignment_res_mapping,
            "jwt_token": jwt_token,
            "request_body": query,
        }
    return services.send_post_back_office(
        **args
    )

def update_assignment_req_mapping(request, hru_id):
    return {
        **base_assignment_action_req(request),
        "I_ASG_SEQ_NUM": request.get("asg_id"),
        "I_ASGD_REVISION_NUM": request.get("revision_num"),
        "I_ASGD_CRITICAL_NEED_IND": "Y" if request.get("critical_need_ind") else "N",
        "I_ASGD_UPDATE_ID": hru_id,
        "I_ASGD_UPDATE_DATE": request.get("updated_date"),
    }

def update_assignment_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for updating assignment failed.')
        return None
    return data
    
def update_separation_req_mapping(request, hru_id):
    return {
        **base_separation_action_req(request),
        "I_SEP_SEQ_NUM": request.get("sep_id"),
        "I_SEPD_REVISION_NUM": request.get("revision_num"),
        "I_SEPD_UPDATE_ID": hru_id,
        "I_SEPD_UPDATE_DATE": request.get("updated_date"),
        "O_SEPD_REVISION_NUM": "",
        "O_RETURN_CODE": "",
        "QRY_ACTION_DATA": "",
        "QRY_ERROR_DATA": "",
    }

def update_separation_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for updating separation failed.')
        return None
    return data


# ======== Create Assignment/Separation ========

def create_assignment_separation(query, jwt_token, is_separation):
    '''
    Create Assignment or Separation
    '''
    if is_separation:
        args = {
            "proc_name": 'act_addsep',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": create_separation_req_mapping,
            "response_mapping_function": create_separation_res_mapping,
            "jwt_token": jwt_token,
            "request_body": query,
        }
    else:
        args = {
            "proc_name": 'qry_addasg',
            "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
            "request_mapping_function": create_assignment_req_mapping,
            "response_mapping_function": create_assignment_res_mapping,
            "jwt_token": jwt_token,
            "request_body": query,
        }

    return services.send_post_back_office(
        **args
    )

def create_assignment_req_mapping(request):
    return {
        **base_assignment_action_req(request),
        "I_EMP_SEQ_NBR": request.get("employee"),
        "I_POS_SEQ_NUM": request.get("position"),
    }

def create_assignment_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for creating assignment failed.')
        return None
    return data

def create_separation_req_mapping(request):
    return {
        **base_separation_action_req(request),
        "I_EMP_SEQ_NBR": request.get("employee"),
    }

def create_separation_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for creating separation failed.')
        return None
    return data
