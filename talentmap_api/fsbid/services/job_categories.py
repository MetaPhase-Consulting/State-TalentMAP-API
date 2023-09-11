import logging
import pydash
from copy import deepcopy
from django.conf import settings
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services, employee

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL

# FILTERS

# def get_post_access_filters(jwt_token):
#     '''
#     Gets Filters for Search Post Access Page
#     '''
#     args = {
#         "proc_name": 'prc_lst_bureau_org_tree',
#         "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
#         "request_body": {},
#         "request_mapping_function": spa_filter_req_mapping,
#         "response_mapping_function": spa_filter_res_mapping,
#         "jwt_token": jwt_token,
#     }
#     return services.send_post_back_office(
#         **args
#     )

# def spa_filter_req_mapping(request):
#     return {
#         "PV_API_VERSION_I": '',
#         "PV_AD_ID_I": '',
#     }

# def spa_filter_res_mapping(data):
#     def bureau_map(x):
#         return {
#             'code': x.get('Bureau'),
#             'description': x.get('ORG_SHORT_DESC'),
#         }
#     def person_map(x):
#         return {
#             'code': x.get('PER_SEQ_NUM'),
#             'description': x.get('PER_FULL_NAME'),
#         }
#     def role_map(x):
#         return {
#             'code': x.get('ROLE_CODE'),
#             'description': x.get('ROLE_DESC'),
#         }
#     def org_map(x):
#         return {
#             'code': x.get('Org'),
#             'description': x.get('ORG_DESC'),
#         }
#     def location_map(x):
#         return {
#             'code': x.get('COUNTRY_STATE_CODE'),
#             'description': x.get('COUNTRY_STATE_DESC'),
#         }
#     def position_map(x):
#         return {
#             'code': x.get('POS_SEQ_NUM'),
#             'description': x.get('POS_NUM_TEXT'),
#         }

#     return {
#         'bureauFilters': list(map(bureau_map, data.get('PQRY_BUREAU_LEVEL_O'))),
#         'personFilters': list(map(person_map, data.get('PQRY_PERSON_LEVEL_O'))),
#         'roleFilters': list(map(role_map, data.get('PQRY_POST_ROLE_O'))),
#         'positionFilters': list(map(position_map, data.get('PQRY_POSITION_LEVEL_O'))),
#         'locationFilters': list(map(location_map, data.get('PQRY_COUNTRY_O'))),
#         'orgFilters': list(map(org_map, data.get('PQRY_ORG_LEVEL_O'))),
#     }


def get_job_categories_data(jwt_token, request):
    '''
    Gets a list of all Job Categories
    '''
    args = {
        "proc_name": 'qry_lstJobCats',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        # "request_mapping_function": map_job_categories_query,
        "response_mapping_function": fsbid_to_tm_jc_data_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def get_job_category_skills(jwt_token, request):
    '''
    Gets a list of Skills associated with a Job Category
    '''
    args = {
        "proc_name": 'qry_getJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        # "request_mapping_function": map_job_categories_query,
        "response_mapping_function": fsbid_to_tm_jc_skills_data_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def fsbid_to_tm_jc_data_mapping(data):
    def jc_results_mapping(x):
        return {
            'id': x.get('JC_ID') or '-',
            'description': x.get('JC_NM_TXT') or 'None Listed',
        }
    return list(map(jc_results_mapping, data.get('QRY_LSTJOBCATS_REF')))

def format_request_data_to_string(request_values, table_key):
    data_entries = []
    for item in request_values.split(","):
        data_entry = f'"Data": {{"{table_key}": "{item}"}}'
        data_entries.append(data_entry)

    result_string = "{" + ",".join(data_entries) + "}"
    return result_string


def map_search_post_access_query():
    mapped_request = {
      "PV_API_VERSION_I": "2", 
      "PV_AD_ID_I": "",
      "QRY_LSTJOBCATS_REF": "",
    }

    return mapped_request


# POST REQUEST


# def remove_post_access_permissions(jwt_token, request):
#     '''
#     Remove Access for a Post
#     '''
#     args = {
#         "proc_name": 'prc_mod_org_access',
#         "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
#         "request_body": request,
#         "request_mapping_function": map_search_post_access_post_request,
#         "response_mapping_function": None,
#         "jwt_token": jwt_token,

#     }
#     return services.send_post_back_office(
#         **args
#     )

# def map_search_post_access_post_request(req):
#     mapped_request = {
#       "PV_API_VERSION_I": "2",  
#     }
    
#     mapped_request['PJSON_ORG_ACCESS_I'] = format_request_post_data_to_string(req, 'BOAID')
#     return mapped_request

# def format_request_post_data_to_string(request_values, table_key):
#     data_entries = []
#     for item in request_values:
#         data_entry = f'"Data": {{"{table_key}": "{item}", "ACTION": "D"}}'
#         data_entries.append(data_entry)

#     result_string = "{" + ",".join(data_entries) + "}"
#     return result_string

