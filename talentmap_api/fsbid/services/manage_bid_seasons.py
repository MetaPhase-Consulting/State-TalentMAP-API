from django.conf import settings
from talentmap_api.fsbid.services import common as services

WS_ROOT = settings.WS_ROOT_API_URL

def get_bid_seasons_data(jwt_token, request):
    '''
    Gets data for Bid Seasons
    '''
    args = {
        "proc_name": 'prc_lst_bid_season',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": map_manage_bid_seasons_query,
        "response_mapping_function": fsbid_to_tm_mbs_data_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def map_manage_bid_seasons_query(req):
    mapped_request = {
      "PV_API_VERSION_I": "2",  
    }
    return mapped_request

def fsbid_to_tm_mbs_data_mapping(data):
    def bsm_results_mapping(x):
        return {
            'id': x.get('BSN_ID') or '---',
            'description': x.get('BSN_DESCR_TEXT') or '---',
            'bid_seasons_begin_date': x.get('BSN_START_DATE') or '---',
            'bid_seasons_end_date': x.get('BSN_END_DATE') or '---',
            'bid_seasons_panel_cutoff': x.get('BSN_PANEL_CUTOFF_DATE') or '---',
            'bid_seasons_future_vacancy': x.get('BSN_FUTURE_VACANCY_IND') or '---',
        }
    return list(map(bsm_results_mapping, data.get('PQRY_CUST_BSN_TAB_O')))



def update_bid_seasons_data(jwt_token, request):
    '''
    Update Bid Season
    '''
    args = {
    "proc_name": 'prc_iud_bid_season',
    "package_name": 'PKG_WEBAPI_WRAP',
    "request_body": request,
    "request_mapping_function": map_bid_season_post_request,
    "response_mapping_function": None,
    "jwt_token": jwt_token,
    }

    return services.send_post_back_office(
        **args
    )

def map_bid_season_post_request(req):
    mapped_request = {
      "PV_API_VERSION_I": "2",  
    }
    
    mapped_request['PJSON_ORG_ACCESS_I'] = format_request_post_data_to_string(req, 'BOAID')
    return mapped_request

def format_request_post_data_to_string(request_values, table_key):
    data_entries = []
    for item in request_values:
        data_entry = f'"Data": {{"{table_key}": "{item}", "ACTION": "D"}}'
        data_entries.append(data_entry)

    result_string = "{" + ",".join(data_entries) + "}"
    return result_string
