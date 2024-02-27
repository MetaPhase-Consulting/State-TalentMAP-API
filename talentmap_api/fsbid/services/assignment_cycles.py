import logging
import pydash
from datetime import datetime as dt
from django.conf import settings
from talentmap_api.fsbid.services import common as services
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL


def get_assignment_cycles_data(jwt_token, request):
    '''
    Gets the Data for the Assignment Cycle Management Page
    '''
    args = {
        "proc_name": 'qry_lstassigncycles',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
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
    return list(map(results_mapping, data.get('QRY_LSTASSIGNCYCLES_REF')))


def create_assignment_cycle(jwt_token, request):
    '''
    Create a new Assignment Cycle for the Cycle Management Page
    '''
    args = {
        "proc_name": 'act_addassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_body": request,
        "request_mapping_function": create_assignment_cycles_req_mapping,
        "response_mapping_function": create_assignment_cycles_res_mapping,
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

def create_assignment_cycles_req_mapping(req):
    data = req['data']
    name = data['assignmentCycle']
    cycle_category = data['cycleCategory']
    cycle_status = data['cycleStatus']
    exclusive_position = 'Y' if data['exclusivePosition'] else 'N'
    post_viewable = 'Y' if data['postViewable'] else 'N'


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

    # keep until tested in dev
    logger.info('-------- assignment_cycles_req_mapping --------')
    logger.info(mapped_request)
    logger.info('-----------------------')
    print('🐥🐥🐥🐥🐥🐥🐥🐥🐥🐥️')
    print(mapped_request)
    print('🐥🐥🐥🐥🐥🐥🐥🐥🐥🐥️')

    return mapped_request


def create_assignment_cycles_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        return Response(status=status.HTTP_400_BAD_REQUEST, data='There was an error attempting to create this Assignment Cycle. Please try again.')
    return Response(data)


def get_assignment_cycle_data(jwt_token, pk):
    '''
    Gets the Data for single Assignment Cycle
    '''
    args = {
        "proc_name": 'qry_getassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
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

    def get_value_from_ref(data_set, value):
        for item in data_set:
            if item['value'] == value:
                return item

    dates_mapped = {}
    for item in data.get('QRY_LSTCYCLEDATE_REF'):
        name = item['CDT_CD']
        dates_mapped[name] = dates_mapping(item)

    cycle_status_reference = list(map(cycle_status_mapping, data.get('QRY_LSTCYCLESTATUS_REF')))
    cycle_category_reference = list(map(cycle_category_mapping, data.get('QRY_LSTCYCLECATEGORY_REF')))

    results = {
        'cycle_name': data.get('O_CYCLE_NM_TXT'),
        'last_updated': data.get('O_CYCLE_LAST_UPDT_TMSMP_DT'),
        'exclusive_position': data.get('O_CYCLE_EXCLUSIVE_POS_FLG'),
        'post_viewable': data.get('O_CYCLE_POST_VIEWABLE_IND'),
        'cycle_category': get_value_from_ref(cycle_category_reference, data.get('O_CC_CD')),
        'cycle_status': get_value_from_ref(cycle_status_reference, data.get('O_CS_CD')),
        'dates_mapping': dates_mapped,
        'cycle_status_reference': cycle_status_reference,
        'cycle_category_reference': cycle_category_reference,
    }
    return results


def post_assignment_cycle_positions(jwt_token, pk):
    '''
    Post Open Positions for an Assignment Cycle
    '''
    args = {
        "proc_name": 'act_modpostassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_body": pk,
        "request_mapping_function": assignment_cycle_req_mapping,  # SHOULD work
        "response_mapping_function": post_positions_res_mapping,  # double check in dev
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def post_positions_res_mapping(data):
    # double check in dev
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        return Response(status=status.HTTP_400_BAD_REQUEST, data='There was an error attempting to Post the Open Positions for this Assignment Cycle. Please try again.')
    return Response(data)


def update_assignment_cycle(jwt_token, request):
    '''
    Update existing Assignment Cycle for the Cycle Management Page
    '''
    args = {
        "proc_name": 'act_modAssignCycle',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_body": request,
        "request_mapping_function": create_assignment_cycles_req_mapping,  # MIGHT work
        "response_mapping_function": update_assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_assignment_cycles_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        return Response(status=status.HTTP_400_BAD_REQUEST, data='There was an error attempting to update this Assignment Cycle. Please try again.')
    return Response(data)
