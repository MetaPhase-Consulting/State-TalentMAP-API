import logging
from django.conf import settings
from talentmap_api.fsbid.services import common as services
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL

def get_bid_seasons_data(jwt_token, request):
    '''
    Gets data for Bid Seasons
    '''
    args = {
        "proc_name": 'prc_lst_bid_seasons',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_body": request,
        "request_mapping_function": bid_seasons_data_req_mapping,
        "response_mapping_function": bid_seasons_data_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def bid_seasons_data_req_mapping(req):
    mapped_request = {
      "PV_API_VERSION_I": "",
    }
    return mapped_request

def bid_seasons_data_res_mapping(data):
    def bsm_results_mapping(x):
        return {
            'id': x.get('BSN_ID') or None,
            'description': x.get('BSN_DESCR_TEXT') or None,
            'bidSeasonsBeginDate': x.get('BSN_START_DATE') or None,
            'bidSeasonsEndDate': x.get('BSN_END_DATE') or None,
            'bidSeasonsPanelCutoff': x.get('BSN_PANEL_CUTOFF_DATE') or None,
            'bidSeasonsFutureVacancy': x.get('BSN_FUTURE_VACANCY_IND') or 'N',
            'bidSeasonsSntSeqNum': x.get('SNT_SEQ_NUM') or '1',
            'bidSeasonsCreateId': x.get('BSN_CREATE_ID') or None,
            'bidSeasonsCreateDate': x.get('BSN_CREATE_DATE') or None,
            'bidSeasonsUpdateId': x.get('BSN_UPDATE_ID') or None,
            'bidSeasonsUpdateDate': x.get('BSN_UPDATE_DATE') or None,
        }
    return list(map(bsm_results_mapping, data.get('PQRY_CUST_BSN_TAB_O')))



def update_bid_seasons_data(jwt_token, request):
    '''
    Update Bid Season
    '''
    args = {
    "proc_name": 'prc_iud_bid_season',
    "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
    "request_body": request,
    "request_mapping_function": update_bid_seasons_data_req_mapping,
    "response_mapping_function": update_bid_seasons_data_res_mapping,
    "jwt_token": jwt_token,
    }

    return services.send_post_back_office(
        **args
    )


def update_bid_seasons_data_res_mapping(data):
    if data is None or (data['PV_RETURN_CODE_O'] and data['PV_RETURN_CODE_O'] is not 0):
        error_message = data['PQRY_ERROR_DATA_O'][0]['MSG_TXT']
        if error_message == 'The bid season dates cannot overlap an existing bid season.':
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='There was an error attempting to update/create this Bid Season. Please try again.')
    return Response(data)


def update_bid_seasons_data_req_mapping(req):
    isUpdate = True if ('id' in req['data'] and req['data']['id'] is not None) else False # Insert will not pass an ID

    mapped_request = {
      "PV_API_VERSION_I": "",
      "PV_AD_ID_I": "",
      "PV_ACTION_I": "U" if isUpdate else "I",
    }

    mapped_request['PTYP_CUST_BSN_TAB_I'] = format_request_post_data_to_string(req, isUpdate)
    return mapped_request


def format_request_post_data_to_string(request, isUpdate):
    id = request['data']['id'] if isUpdate else ''
    name = request['data']['name']
    start_date = request['data']['startDate'][:10]
    end_date = request['data']['endDate'][:10]
    panel_cutoff_date = request['data']['panelCutoffDate'][:10]
    future_vacancy = request['data']['futureVacancy']
    snt_seq_num = request['data']['season']
    # below values are required for UPDATE, but not for INSERT
    create_id = request['data']['bidSeasonsCreateId'] if isUpdate else ""
    create_date = request['data']['bidSeasonsCreateDate'][:10] if isUpdate else ""
    update_id = request['data']['bidSeasonsUpdateId'] if isUpdate else ""
    update_date = request['data']['bidSeasonsUpdateDate'][:10] if isUpdate else ""

    new_dict = {
      "Data": [{
          "BSN_ID": id,
          "BSN_DESCR_TEXT": name,
          "BSN_START_DATE": start_date,
          "BSN_END_DATE": end_date,
          "BSN_PANEL_CUTOFF_DATE": panel_cutoff_date,
          "BSN_FUTURE_VACANCY_IND": future_vacancy,
          "SNT_SEQ_NUM": snt_seq_num,
          "BSN_CREATE_ID": create_id,
          "BSN_CREATE_DATE": create_date,
          "BSN_UPDATE_ID": update_id,
          "BSN_UPDATE_DATE": update_date,
      }]
    }
    return new_dict
