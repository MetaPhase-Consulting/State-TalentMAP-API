import logging
from functools import partial

import pydash
import jwt

from django.conf import settings

from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response

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
        "I_PM_SEQ_NUM": request,
    }

def panel_meeting_response_mapping(response):
    def dates(x):
        return {
            'code': x.get('MDT_CODE'),
            'description': x.get('MDT_DESC_TEXT'),
            'date': x.get('PMD_DTTM'),
        }
    def success_mapping(x):
        return {
            'panel_id': x.get('O_PM_SEQ_NUM'),
            'type_code': x.get('O_PMT_CODE'),
            'type_description': x.get('O_PMT_DESC_TEXT'),
            'status_code': x.get('O_PMS_CODE'),
            'status_description': x.get('O_PMS_DESC_TEXT'),
            'panel_dates': list(map(dates, x.get('QRY_LSTPMD_REF'))),
        }
    return service_response(response, 'Panel Meeting Data', success_mapping)


# ======================== Create Panel Meeting ========================

def modify_panel_meeting_and_dates(query, jwt_token):
    '''
    Modify Panel Meeting and Panel Meeting Dates
    '''
    # Inject decoded hru
    query['hru_id'] = jwt.decode(jwt_token, verify=False).get('sub')

    # Unpack requested changes 
    panel_type = query.get("panelMeetingType")
    panel_status = query.get("panelMeetingStatus")
    panel_date = query.get("panelMeetingDate")
    add_date = query.get("addendumCutoff")
    cut_date = query.get("prelimCutoff")

    # Unpack original resource 
    ref = query.get("originalReference", {})
    refDates = ref.get("panelMeetingDates", {})

    # Check for existing panel meeting
    existing_pm_seq_num = ref.get("pm_seq_num")
    # Change back to none
    newly_created_pm_seq_num = None

    if panel_status or panel_type:
        if not existing_pm_seq_num:
            panel_meeting = create_panel_meeting(query, jwt_token)
            newly_created_pm_seq_num = pydash.get(panel_meeting, "[0].pm_seq_num", None)
        elif (panel_status != ref.get("pms_code")) or (panel_type != ref.get("pmt_code")):
             panel_meeting = edit_panel_meeting(query, jwt_token)
           
    if existing_pm_seq_num or newly_created_pm_seq_num:
        query["pmdpmseqnum"] = existing_pm_seq_num if existing_pm_seq_num else newly_created_pm_seq_num

        meet = dict(*filter(lambda x: x.get("mdt_code", "") == "MEET", refDates))
        add = dict(*filter(lambda x: x.get("mdt_code", "") == "ADD", refDates))
        cut = dict(*filter(lambda x: x.get("mdt_code", "") == "CUT", refDates))

        if panel_date:
            if not meet:
                create_panel_meeting_date(query, panel_date, "MEET", jwt_token)
            elif panel_date != meet.get("pmd_dttm"):
                edit_panel_meeting_date(query, panel_date, meet, jwt_token)
        if add_date:
            if not add:
                create_panel_meeting_date(query, add_date, "ADD", jwt_token)
            elif add_date != add.get("pmd_dttm"):
                edit_panel_meeting_date(query, add_date, add, jwt_token)
        if cut_date:
            if not cut:
                create_panel_meeting_date(query, cut_date, "CUT", jwt_token)
            elif cut_date != cut.get("pmd_dttm"):
                edit_panel_meeting_date(query, cut_date, cut, jwt_token)
    else:
        logger.error("PM create failed")


def edit_pmd_mapping(query, date, original_data):
    mapped_query = {
        "pmdpmseqnum": query.get("pmdpmseqnum"),
        "pmdmdtcode": original_data.get("mdt_code"),
        "pmddttm": date.replace("T", " "),
        "pmdupdatedate": original_data.get("pmd_update_date", "").replace("T", " "),
        "pmdupdateid": query.get("hru_id"),
        "pmdcreatedate": original_data.get("pmd_create_date", "").replace("T", " "),
        "pmdcreateid": original_data.get("pmd_create_id"),
    }
    return mapped_query


def create_panel_meeting(query, jwt_token):
    args = {
        "uri": "v1/panels/meeting",
        "query": query,
        "query_mapping_function": convert_panel_meeting_create_query,
        "jwt_token": jwt_token,
        "mapping_function": None,
    }

    return services.get_results_with_post(
        **args
    )


def create_panel_meeting_date(query, date, date_type, jwt_token):
    pmseqnum = query.get("pmdpmseqnum")
    args = {
        "uri": f"v1/panels/meeting/{pmseqnum}/dates",
        "query": query,
        "query_mapping_function": partial(create_pmd_mapping, date=date, date_type=date_type),
        "jwt_token": jwt_token,
        "mapping_function": None,
    }

    return services.get_results_with_post(
        **args
    )


def convert_panel_meeting_create_query(query):
    hru_id = query.get("hru_id")
    mapped_query = {
        "pmvirtualind": "N",
        "pmcreateid": hru_id,
        "pmupdateid": hru_id,
        "pmpmscode": query.get("panelMeetingStatus", "I"),
        "pmpmtcode": query.get("panelMeetingType", "ID"),
    }
    return mapped_query


def create_pmd_mapping(query, date, date_type):
    hru_id = query.get("hru_id")
    mapped_query = {
        "pmdpmseqnum": query.get("pmdpmseqnum"),
        "pmdmdtcode": date_type,
        "pmddttm": date.replace("T", " "),
        "pmdupdateid": hru_id,
        "pmdcreateid": hru_id,
    }
    return mapped_query



# ======================== Edit Panel Meeting ========================
def edit_panel_meeting(query, jwt_token):
    pmseqnum = query.get("originalReference", {}).get("pm_seq_num")
    args = {
        "uri": f"v1/panels/meeting/{pmseqnum}",
        "query": query,
        "query_mapping_function": convert_panel_meeting_edit_query,
        "jwt_token": jwt_token,
        "mapping_function": None,
    }
    return services.send_put_request(
        **args
    )


def edit_panel_meeting_date(query, date, original_data, jwt_token):
    pmseqnum = query.get("pmdpmseqnum")
    args = {
        "uri": f"v1/panels/meeting/{pmseqnum}/dates",
        "query": query,
        "query_mapping_function": partial(edit_pmd_mapping, date=date, original_data=original_data),
        "jwt_token": jwt_token,
        "mapping_function": None,
    }

    return services.send_put_request(
        **args
    )


def convert_panel_meeting_edit_query(query):
    # ref is data from the originally created resource required for subsequent edits
    ref = query.get("originalReference", {})
    mapped_query = {
        "pmseqnum": ref.get("pm_seq_num"),
        "pmvirtualind": "N",
        "pmcreateid": ref.get("pm_create_id"),
        "pmupdateid": query.get("hru_id"),
        "pmcreatedate": ref.get("pm_create_date").replace("T", " "),
        "pmupdatedate": ref.get("pm_update_date").replace("T", " "),
        "pmpmscode": query.get("panelMeetingStatus"),
        "pmpmtcode": query.get("panelMeetingType"),
    }
    return mapped_query


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
    def success_mapping(x):
        return {
            'statuses': list(map(statuses, x.get('QRY_LSTAIS_DD_REF'))),
            'values': list(map(values, x.get('QRY_MODPOSTPNL_REF'))),
        }
    return service_response(response, 'Post Panel Processing Data', success_mapping)

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
        "I_AI_SEQ_NUM": request.get('sequence_number'),
        "I_AI_UPDATE_ID": request.get('update_id'),
        "I_AI_UPDATE_DATE": request.get('update_date'),
        "I_AI_AIS_CODE": ais_code
    }

def edit_post_panel_res_mapping(data):
    return service_response(data, 'Post Panel Processing Edit')

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
        "I_PM_SEQ_NUM": request,
    }

def run_preliminary_res_mapping(data):
    return service_response(data, 'Run Official Preliminary')

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
    return service_response(data, 'Run Official Addendum')

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
    return service_response(data, 'Run Post Panel')
