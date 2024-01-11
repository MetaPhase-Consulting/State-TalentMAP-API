import logging
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
    date_object = dt.strptime(input_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    # Format the date as MM/dd/yyyy
    formatted_date = date_object.strftime("%m/%d/%Y")
    return formatted_date

def create_assignment_cycles_req_mapping(req):
    name = req['data']['assignmentCycle']
    cycle_category = req['data']['cycleCategory']
    cycle_status = req['data']['cycleStatus']
    exclusive_positions = "Y" if req['data']['exclusivePositions'] else "N"
    post_viewable = "Y" if req['data']['postViewable'] else "N"

    cycle_boundries = format_date_string(req['data']['cycleBoundries'][0])
    six_month_language = format_date_string(req['data']['sixMonthLanguage'][0])
    twelve_month_language = format_date_string(req['data']['twelveMonthLanguage'][0])
    twenty_four_month_language = format_date_string(req['data']['twentyFourMonthLanguage'][0])
    bureau_position_review = format_date_string(req['data']['bureauPositionReview'])
    bidding_start = format_date_string(req['data']['biddingStart'])
    bid_due = format_date_string(req['data']['bidDue'])
    bureau_pre_season_bid_review = format_date_string(req['data']['bureauPreSeasonBidReview'])
    bureau_early_season_bid_review = format_date_string(req['data']['bureauEarlySeasonBidReview'])
    bureau_bid_review = format_date_string(req['data']['bureauBidReview'])
    bid_audit = format_date_string(req['data']['bidAudit'])
    bid_book_review = format_date_string(req['data']['bidBookReview'])
    bid_count_review = format_date_string(req['data']['bidCountReview'])
    htf_review = format_date_string(req['data']['htfReview'])
    organization_count_review = format_date_string(req['data']['organizationCountReview'])
    mds_review = format_date_string(req['data']['mdsReview'])
    assigned_bidder = format_date_string(req['data']['assignedBidder'])
    start_dates_string = ",".join(
        [
            cycle_boundries,
            six_month_language,
            twelve_month_language,
            twenty_four_month_language,
            bureau_position_review,
            bidding_start,
            bid_due,
            bureau_pre_season_bid_review,
            bureau_early_season_bid_review,
            bureau_bid_review,
            bid_audit,
            bid_book_review,
            bid_count_review,
            htf_review,
            organization_count_review,
            mds_review,
            assigned_bidder,
        ]
    )
    cycle_boundries_end = format_date_string(req['data']['cycleBoundries'][1])
    six_month_language_end = format_date_string(req['data']['sixMonthLanguage'][1])
    twelve_month_language_end = format_date_string(req['data']['twelveMonthLanguage'][1])
    twenty_four_month_language_end = format_date_string(req['data']['twentyFourMonthLanguage'][1])
    end_dates_string = ",".join([cycle_boundries_end, six_month_language_end, twelve_month_language_end, twenty_four_month_language_end])

    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
        "i_cycle_nm_txt": name,
        "i_cc_cd": cycle_category,
        "i_cs_cd": cycle_status,
        "i_cycle_exclusive_pos_flg": exclusive_positions,
        "i_cycle_post_viewable_ind": post_viewable,
        "i_cdt_cd": "CYCLE,6MOLANG,12MOLANG,24MOLANG,BURPOS,BIDSTART,BIDDUE,BURPREBD,BUREARLY,BURBID,BIDAUDIT,BIDBOOK,BIDCOUNT,BIDHTF,BIDORG,BIDMDS,PANLASG",
    }
    mapped_request['i_cd_bgn_dt'] = start_dates_string
    mapped_request['i_cd_end_dt'] = end_dates_string + ",,,,,,,,,,,,,"
    return mapped_request


def create_assignment_cycles_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        return Response(status=status.HTTP_400_BAD_REQUEST, data='There was an error attempting to create this Assignment Cycle. Please try again.')
    return Response(data)
