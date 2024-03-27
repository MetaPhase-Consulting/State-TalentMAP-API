from datetime import datetime as dt
from functools import partial
import logging
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response
import pydash
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL


def get_assignment_cycles_data(jwt_token, request):
    '''
    Gets the Data for the Assignment Cycle Management Page
    '''
    args = {
        "proc_name": 'qry_lstassigncycles',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": assignment_cycles_req_mapping,
        "response_mapping_function": assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def assignment_cycles_req_mapping(request):
    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
    }
    return mapped_request


def assignment_cycles_res_mapping(data):
    def results_mapping(x):
        return {
            'id': x.get('CYCLE_ID') or None,
            'name': x.get('CYCLE_NM_TXT') or None,
            'status': x.get('CS_DESCR_TXT') or None,
            'category': x.get('CC_DESCR_TXT') or None,
            'begin_date': x.get('CD_BGN_DT') or None,
            'end_date': x.get('CD_END_DT') or None,
            'excl_position': x.get('CYCLE_EXCLUSIVE_POS_FLG') or None,
            'post_view': x.get('CYCLE_POST_VIEWABLE_IND') or None,
        }

    def success_mapping(x):
        return list(map(results_mapping, x.get('QRY_LSTASSIGNCYCLES_REF')))

    return service_response(data, 'Assignment Cycles Get Cycles', success_mapping)


def create_assignment_cycle(jwt_token, request):
    '''
    Create a new Assignment Cycle for the Cycle Management Page
    '''
    args = {
        "proc_name": 'act_addassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": save_assignment_cycle_req_mapping,
        "response_mapping_function": create_assignment_cycle_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def format_date_string(input_date):
    if input_date == '':
        return input_date
    if len(input_date) == 10:
        return input_date
    date_object = dt.strptime(input_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    # Format the date as MM/dd/yyyy (unless it already is)
    formatted_date = date_object.strftime("%m/%d/%Y")
    return formatted_date


def save_assignment_cycle_req_mapping(req, is_update=False):
    data = req['data']
    name = data['assignmentCycle']
    cycle_category = data['cycleCategory']
    cycle_status = data['cycleStatus']
    exclusive_position = data['exclusivePosition']
    post_viewable = data['postViewable']


    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_nm_txt': name,
        'i_cc_cd': cycle_category,
        'i_cs_cd': cycle_status,
        'i_cycle_exclusive_pos_flg': exclusive_position,
        'i_cycle_post_viewable_ind': post_viewable,
    }

    cdt_bgn_end_dict = {
        'CYCLE': [format_date_string(pydash.get(req, 'data.cycleBoundries[0]') or ''), format_date_string(pydash.get(req, 'data.cycleBoundries[1]') or '')],
        '6MOLANG': [format_date_string(pydash.get(req, 'data.sixMonthLanguage[0]') or ''), format_date_string(pydash.get(req, 'data.sixMonthLanguage[1]') or '')],
        '12MOLANG': [format_date_string(pydash.get(req, 'data.twelveMonthLanguage[0]') or ''), format_date_string(pydash.get(req, 'data.twelveMonthLanguage[1]') or '')],
        '24MOLANG': [format_date_string(pydash.get(req, 'data.twentyFourMonthLanguage[0]') or ''), format_date_string(pydash.get(req, 'data.twentyFourMonthLanguage[1]') or '')],
        'BURPOS': format_date_string(req['data']['bureauPositionReview']),
        'BIDSTART': format_date_string(req['data']['biddingStart']),
        'BIDDUE': format_date_string(req['data']['bidDue']),
        'BURPREBD': format_date_string(req['data']['bureauPreSeasonBidReview']),
        'BUREARLY': format_date_string(req['data']['bureauEarlySeasonBidReview']),
        'BURBID': format_date_string(req['data']['bureauBidReview']),
        'BIDAUDIT': format_date_string(req['data']['bidAudit']),
        'BIDBOOK': format_date_string(req['data']['bidBookReview']),
        'BIDCOUNT': format_date_string(req['data']['bidCountReview']),
        'BIDHTF': format_date_string(req['data']['htfReview']),
        'BIDORG': format_date_string(req['data']['organizationCountReview']),
        'BIDMDS': format_date_string(req['data']['mdsReview']),
        'PANLASG': format_date_string(req['data']['assignedBidder']),
    }


    cdt = []
    cd_bgn = []
    cd_end = []

    for x in cdt_bgn_end_dict:
        if isinstance(cdt_bgn_end_dict[x], list):
            if cdt_bgn_end_dict[x].count('') < 2:
                cdt.append(x)
                cd_bgn.append(cdt_bgn_end_dict[x][0])
                cd_end.append(cdt_bgn_end_dict[x][1])
        elif (cdt_bgn_end_dict[x] != ''):
            cdt.append(x)
            cd_bgn.append(cdt_bgn_end_dict[x])
            cd_end.append('')

    mapped_request['i_cdt_cd'] = ','.join(cdt)
    mapped_request['i_cd_bgn_dt'] = ','.join(cd_bgn)
    mapped_request['i_cd_end_dt'] = ','.join(cd_end)

    if is_update:
        mapped_request['I_CYCLE_ID'] = data['cycleId']
        mapped_request['I_CYCLE_LAST_UPDT_TMSMP_DT'] = data['stampDate']
        mapped_request['I_CYCLE_LAST_UPDT_USER_ID'] = data['stampId']
        mapped_request['I_CD_LAST_UPDT_TMSMP_DT'] = data['stampStrings']
        mapped_request['I_CD_LAST_UPDT_USER_ID'] = data['stampIdStrings']
        mapped_request['O_RETURN_CODE'] = ''
        mapped_request['QRY_ACTION_DATA'] = ''
        mapped_request['QRY_ERROR_DATA'] = ''

    return mapped_request


def create_assignment_cycle_res_mapping(data):
    return service_response(data, 'Assignment Cycles Create Cycle')


def get_assignment_cycle_data(jwt_token, pk):
    '''
    Gets the Data for single Assignment Cycle
    '''
    args = {
        "proc_name": 'qry_getassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": pk,
        "request_mapping_function": assignment_cycle_req_mapping,
        "response_mapping_function": assignment_cycle_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def assignment_cycle_req_mapping(pk):
    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
        "i_cycle_id": pk
    }
    return mapped_request


def assignment_cycle_res_mapping(data):
    def dates_mapping(x):
        return {
            'description_text': x.get('CDT_DESCR_TXT') or None,
            'begin_date': x.get('CD_BGN_DT') or None,
            'end_date': x.get('CD_END_DT') or None,
            'sort_order': x.get('CDT_SORT_ORDER_NUM') or None,
            'last_update_stamp': x.get('CD_LAST_UPDT_TMSMP_DT') or None,
            'last_update_id': x.get('CD_LAST_UPDT_USER_ID') or None,
        }

    def cycle_status_mapping(x):
        return {
            'label': x.get('CS_DESCR_TXT') or None,
            'value': x.get('CS_CD') or None,
        }

    def cycle_category_mapping(x):
        return {
            'label': x.get('CC_DESCR_TXT') or None,
            'value': x.get('CC_CD') or None,
        }

    def success_mapping(x):
        dates_mapped = {}
        update_timestamps = []
        id_timestamps = []

        for item in x.get('QRY_LSTCYCLEDATE_REF'):
            name = item['CDT_CD']
            dates_mapped[name] = dates_mapping(item)
            update_timestamps.append(str(item['CD_LAST_UPDT_TMSMP_DT']))
            id_timestamps.append(str(item['CD_LAST_UPDT_USER_ID']))

        cycle_status_reference = list(map(cycle_status_mapping, x.get('QRY_LSTCYCLESTATUS_REF')))
        cycle_category_reference = list(map(cycle_category_mapping, x.get('QRY_LSTCYCLECATEGORY_REF')))

        string_stamps = ",".join(update_timestamps)
        string_ids = ",".join(id_timestamps)

        results = {
            'cycle_name': x.get('O_CYCLE_NM_TXT'),
            'exclusive_position': x.get('O_CYCLE_EXCLUSIVE_POS_FLG'),
            'post_viewable': x.get('O_CYCLE_POST_VIEWABLE_IND'),
            'cycle_category': x.get('O_CC_CD'),
            'cycle_status': x.get('O_CS_CD'),
            'last_updated': x.get('O_CYCLE_LAST_UPDT_TMSMP_DT'),
            'last_updated_id': x.get('O_CYCLE_LAST_UPDT_USER_ID'),
            'dates_mapping': dates_mapped,
            'cycle_status_reference': cycle_status_reference,
            'cycle_category_reference': cycle_category_reference,
            'update_timestamps': string_stamps,
            'id_timestamps': string_ids,
        }
        return results

    return service_response(data, 'Assignment Cycles Get Cycle', success_mapping)


def post_assignment_cycle_positions(jwt_token, pk):
    '''
    Post Open Positions for an Assignment Cycle
    '''
    args = {
        "proc_name": 'act_modpostassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": pk,
        "request_mapping_function": assignment_cycle_req_mapping,
        "response_mapping_function": post_positions_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def post_positions_res_mapping(data):
    return service_response(data, 'Assignment Cycles Post Open Positions')


def update_assignment_cycle(jwt_token, request):
    '''
    Update existing Assignment Cycle for the Cycle Management Page
    '''
    args = {
        "proc_name": 'act_modAssignCycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": partial(save_assignment_cycle_req_mapping, is_update=True),
        "response_mapping_function": update_assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_assignment_cycles_res_mapping(data):
    return service_response(data, 'Assignment Cycles Update Cycle')


def delete_assignment_cycle(jwt_token, request):
    '''
    Delete an Assignment Cycle
    '''
    args = {
        "proc_name": 'act_delassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": delete_assignment_cycle_req_mapping,
        "response_mapping_function": update_assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def delete_assignment_cycle_req_mapping(request):
    data = request['data']
    cycleId = data['cycleId']
    timestamp = data['stampDate']
    timestamp_id = data['stampId']
    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
        "i_cycle_id": cycleId,
        "i_cycle_last_updt_tmsmp_dt": timestamp,
        "i_cycle_last_updt_user_id": timestamp_id
    }
    return mapped_request


def merge_assignment_cycles(jwt_token, request):
    '''
    Merge two Assignment Cycles
    '''
    args = {
        "proc_name": 'act_modMergeCycles',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": merge_assignment_cycles_req_mapping,
        "response_mapping_function": update_assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def merge_assignment_cycles_req_mapping(request):
    data = request.get('data')
    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
        "i_source_cycle_id": data.get('sourceCycle'),
        "i_target_cycle_id": data.get('targetCycle'),
    }
    return mapped_request

# --------------------------------------------------------------------------------------- Cycle Positions


def get_cycle_positions_filters(jwt_token):
    '''
    Gets Filters for Cycle Positions Page
    '''
    args = {
        'proc_name': 'qry_lstfsbidSearch',
        'package_name': 'PKG_WEBAPI_WRAP',
        'request_body': {},
        'request_mapping_function': cycle_positions_filter_req_mapping,
        'response_mapping_function': cycle_positions_filter_res_mapping,
        'jwt_token': jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def cycle_positions_filter_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }


def cycle_positions_filter_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Cycle Positions filters failed.")
        return None

    def status_map(x):
        return {
            'code': x.get('CPS_CD'),
            'description': x.get('CPS_DESCR_TXT'),
        }

    def org_map(x):
        return {
            'code': x.get('ORG_CODE'),
            'description': f"{x.get('ORGS_SHORT_DESC')} ({x.get('ORG_CODE')})",
        }

    def skills_map(x):
        return {
            'code': x.get('SKL_CODE'),
            'description': x.get('SKL_DESC'),
        }

    def grade_map(x):
        return {
            'code': x.get('GRD_CD'),
            'description': x.get('GRD_DESCR_TXT'),
        }

    return {
        'statusFilters': list(map(status_map, data.get('QRY_LSTCYCLEPOSSTATUS_DD_REF'))),
        'orgFilters': list(map(org_map, data.get('QRY_LSTORGSHORT_DD_REF'))),
        'skillsFilters': list(map(skills_map, data.get('QRY_LSTSKILLCODES_DD_REF'))),
        'gradeFilters': list(map(grade_map, data.get('QRY_LSTGRADES_DD_REF'))),
    }


def get_cycle_positions(jwt, req):
    '''
    Gets Positions for the Cycle Positions Page
    '''
    args = {
        'proc_name': 'qry_modCyclePos',
        'package_name': 'PKG_WEBAPI_WRAP_SPRINT98',
        'request_body': req,
        'request_mapping_function': cycle_positions_req_mapping,
        'response_mapping_function': cycle_positions_res_mapping,
        'jwt_token': jwt,
    }
    return services.send_post_back_office(
        **args
    )


def cycle_positions_req_mapping(req):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'I_CYCLE_ID': req.get('cycleId'),
        'I_GRD_CD': req.get('grades') or '',
        'I_SKL_CODE_POS': req.get('skills') or '',
        'I_ORG_CODE': req.get('orgs') or '',
        'I_CPS_CD': req.get('statuses') or '',
    }
    return mapped_request


def format_cycle_position_date(input_date):
    if input_date == '' or input_date is None:
        return input_date
    date_object = dt.strptime(input_date, "%Y-%m-%dT%H:%M:%S")
    formatted_date = date_object.strftime("%m/%d/%Y")
    return formatted_date


def cycle_positions_res_mapping(data):
    def position_mapping(x):
        return {
            'id': x.get('CP_ID') or None,
            'position_number': x.get('POS_NUM_TXT') or None,
            'skill_code': x.get('SKL_CODE_POS') or None,
            'skill_desc': x.get('SKL_DESC_POS') or None,
            'title': x.get('PTITLE') or None,
            'org_code': x.get('ORG_CODE') or None,
            'org_desc': x.get('ORGS_SHORT_DESC') or None,
            'grade': x.get('GRD_CD') or None,
            'status': x.get('CPS_DESCR_TXT') or None,
            'languages': x.get('POSLTEXT') or None,
            'bid_cycle': x.get('CYCLE_NM_TXT') or None,
            'ted': x.get('TED') or None,
            'pay_plan': x.get('PPL_CODE') or None,
            'posted_date_formatted': format_cycle_position_date(x.get('CP_POST_DT')) if x.get('CP_POST_DT') else None,
            'posted_date': x.get('CP_POST_DT') or None,
            'incumbent_name': x.get('INCUMBENT_NAME') or None,
            'job_category': x.get('JC_NM_TXT') or None,
            'hard_fill_flag': x.get('ACP_HARD_TO_FILL_IND') or None,
            'crit_need_flag': x.get('CP_CRITICAL_NEED_IND') or None,
        }

    def success_mapping(x):
        return list(map(position_mapping, x.get('QRY_MODCYCLEPOS_REF')))

    return service_response(data, 'Cycle Positions Data', success_mapping)
