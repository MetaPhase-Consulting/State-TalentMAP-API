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
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = [
        "id",
        "position_id",
        "start_date",
        "end_date",
        "asgd_tod_desc_text",
        "asgd_asgs_code",
        "asgd_asgs_text",
        "position",
        "asgd_revision_num",
        "asgd_tod_code",
        "asgd_tod_other_text",
        "asgd_tod_months_num",
        "tod_code",
        "tod_desc_text",
        "tod_months_num",
        "tod_short_desc",
        "tod_status_code",
    ]

    add_these = []

    cols_mapping = {
        "id": "asgdasgseqnum",
        "asg_emp_seq_nbr": "asgempseqnbr",
        "asg_perdet_seq_num": "asgperdetseqnum",
        "position_id": "asgposseqnum",
        "asg_create_id": "asgcreateid",
        "asg_create_date": "asgcreatedate",
        "asg_update_id": "asgupdateid",
        "asg_update_date": "asgupdatedate",
        "asgd_asg_seq_num": "asgdasgseqnum",
        "asgd_revision_num": "asgdrevisionnum",
        "asgd_asgs_text": "asgsdesctext",
        "asgd_asgs_code": "asgdasgscode",
        "asgd_lat_code": "asgdlatcode",
        "asgd_tfcd": "asgdtfcd",
        "asgd_tod_code": "asgdtodcode",
        "asgd_ail_seq_num": "asgdailseqnum",
        "asgd_org_code": "asgdorgcode",
        "asgd_wrt_code_rrrepay": "asgdwrtcoderrrepay",
        "start_date": "asgdetadate",
        "asgd_adjust_months_num": "asgdadjustmonthsnum",
        "end_date": "asgdetdteddate",
        "asgd_salary_reimburse_ind": "asgdsalaryreimburseind",
        "asgd_travelreimburse_ind": "asgdtravelreimburseind",
        "asgd_training_ind": "asgdtrainingind",
        "asgd_create_id": "asgdcreateid",
        "asgd_create_date": "asgdcreatedate",
        "asgd_update_id": "asgdupdateid",
        "asgd_update_date": "asgdupdatedate",
        "asgd_note_comment_text": "asgdnotecommenttext",
        "asgd_priority_ind": "asgdpriorityind",
        "asgd_critical_need_ind": "asgdcriticalneedind",
        "asgs_code": "asgscode",
        "asgs_desc_text": "asgsdesctext",
        "asgs_create_id": "asgscreateid",
        "asgs_create_date": "asgscreatedate",
        "asgs_update_id": "asgsupdateid",
        "asgs_update_date": "asgsupdatedate",
        "position": "position",
        "asgd_tod_other_text": "asgdtodothertext",
        "asgd_tod_months_num": "asgdtodmonthsnum",
        "tod_code": "todcode",
        "tod_desc_text": "toddesctext",
        "tod_months_num": "todmonthsnum",
        "tod_short_desc": "todshortdesc",
        "tod_status_code": "todstatuscode",
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)

def get_assignment_ref_data(data, jwt_token):
    '''
    Get maintain assignment reference data
    '''
    args = {
        "proc_name": 'qry_getAsgDtl',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": asg_ref_data_req_mapping,
        "response_mapping_function": asg_ref_data_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def asg_ref_data_req_mapping(request):
    return {
        "i_asg_seq_num": request.get("asg_id"),
        "i_asgd_revision_num": request.get("revision_num"),
        "pv_api_version_i": "",
        "pv_ad_id_i": "",
    }

def asg_ref_data_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for fetching assignment reference data failed.')
        return None
    return data


def alt_get_assignments(id, jwt_token):
    '''
    Get assignments and separations by perdet from fsbid proc 
    '''
    args = {
        "proc_name": 'qry_lstAsgsSeps',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": alt_asg_req_mapping,
        "response_mapping_function": alt_asg_res_mapping,
        "jwt_token": jwt_token,
        "request_body": { "perdet_seq_num": id },
    }
    return services.send_post_back_office(
        **args
    )
    
def alt_asg_req_mapping(request):
    return {
        "i_pedet_seq_num": request.get("perdet_seq_num"),
        "pv_api_version_i": "",
        "pv_ad_id_i": "",
    }

def alt_asg_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for fetching assignments/separations failed.')
        return None
    return data.get('QRY_LSTASGS_REF')


def alt_update_assignment(query, jwt_token):
    '''
    Get assignments and separations by perdet from fsbid proc 
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    args = {
        "proc_name": 'act_modasgdtl',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": partial(alt_update_asg_req_mapping, hru_id=hru_id),
        "response_mapping_function": alt_update_asg_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
    
def alt_update_asg_req_mapping(request, hru_id):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_ASG_SEQ_NUM": request.get("asg_seq_num"),
        "I_ASGD_REVISION_NUM": request.get("asgd_revision_num"),
        "I_ASGD_ETA_DATE": request.get("eta"),
        "I_ASGD_ETD_TED_DATE": request.get("etd"),
        "I_ASGD_TOD_CODE": request.get("tod"),
        "I_ASGD_TOD_MONTHS_NUM": None,
        "I_ASGD_TOD_OTHER_TEXT": "",
        "I_ASGD_ADJUST_MONTHS_NUM": None,
        "I_ASGD_SALARY_REIMBURSE_IND": "Y" if request.get("salary_reimburse_ind") else "N",
        "I_ASGD_TRAVEL_REIMBURSE_IND": "Y" if request.get("travel_reimburse_ind") else "N",
        "I_ASGD_TRAINING_IND": "Y" if request.get("training_ind") else "N",
        "I_ASGD_CRITICAL_NEED_IND": "Y" if request.get("critical_need_ind") else "N",
        "I_ASGD_ORG_CODE": request.get("org_code"),
        "I_ASGD_ASGS_CODE": request.get("status_code"),
        "I_ASGD_LAT_CODE": request.get("lat_code"),
        "I_ASGD_TF_CD": request.get("travel_code"),
        "I_ASGD_WRT_CODE_RR_REPAY": "Y" if request.get("rr_repay_ind") else "N",
        "I_ASGD_NOTE_COMMENT_TEXT": "",
        "I_ASGD_UPDATE_ID": hru_id,
        "I_ASGD_UPDATE_DATE": request.get("update_date")
    }

def alt_update_asg_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for fetching assignments/separations failed.')
        return None
    return data


def alt_create_assignment(query, jwt_token):
    '''
    Create assignments and separations via fsbid 
    '''
    # TO DO: This does not work until there is more documentation 
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    args = {
        "proc_name": 'qry_addasg',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_mapping_function": partial(alt_update_asg_req_mapping, hru_id=hru_id),
        "response_mapping_function": alt_update_asg_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
    
def alt_create_asg_req_mapping(request, hru_id):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_EMP_SEQ_NBR": "",
        "O_SECREF_ROLE_IND": "",
        "QRY_LSTASGS_REF": "",
        "QRY_LSTLAT_REF": "",
        "QRY_LSTTF_REF": "",
        "QRY_LSTTOD_REF": "",
        "QRY_LSTWRT_REF": "",
        "QRY_LSTBUREAUS_REF": "",
        "QRY_ADDASG_REF": "",
        "O_RETURN_CODE": "",
        "QRY_ACTION_DATA": "",
        "QRY_ERROR_DATA": ""
    }

def alt_create_asg_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for fetching assignments/separations failed.')
        return None
    return data


