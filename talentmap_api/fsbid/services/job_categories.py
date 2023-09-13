import logging
import pydash
from copy import deepcopy
from django.conf import settings
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services, employee

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL

def get_job_categories_data(jwt_token, request):
    '''
    Gets a list of all Job Categories
    '''
    args = {
        "proc_name": 'qry_lstJobCats',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": {},
        "request_mapping_function": map_job_categories_query,
        "response_mapping_function": fsbid_to_tm_jc_data_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def get_job_category_skills(jwt_token, request):
    '''
    Returns all Skills with an indicator field set to 1 on those
    Skills which are associated with the Job Category
    '''
    args = {
        "proc_name": 'qry_getJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": map_jc_skills_query,
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

def fsbid_to_tm_jc_skills_data_mapping(data):
    def jc_skills_results_mapping(x):
        return {
            'code': x.get('SKL_CODE') or '-',
            'description': x.get('SKL_DESC') or 'None Listed',
            'display_skill': x.get('INCLUSION_IND') or 'None Listed'
        }
    return list(map(jc_skills_results_mapping, data.get('QRY_LSTSKILLS_REF')))

def format_request_data_to_string(request_values, table_key):
    data_entries = []
    for item in request_values.split(","):
        data_entry = f'"Data": {{"{table_key}": "{item}"}}'
        data_entries.append(data_entry)

    result_string = "{" + ",".join(data_entries) + "}"
    return result_string


def map_job_categories_query(req):
    mapped_request = {
      "PV_API_VERSION_I": "", 
      "PV_AD_ID_I": "",
      "QRY_LSTJOBCATS_REF": "",
    }

    return mapped_request

def map_jc_skills_query(req):
    mapped_request = {
      "PV_API_VERSION_I": "", 
      "PV_AD_ID_I": "",
      "I_JC_ID": req.get('category_id'),
    }

    return mapped_request

