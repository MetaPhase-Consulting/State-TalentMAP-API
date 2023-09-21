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

def save_new_job_category(jwt_token, request):
    '''
    Saves a new Job Category with skills
    '''
    args = {
        "proc_name": 'act_addJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": map_new_category_query,
        "response_mapping_function": save_new_cat_res_mapping,
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
            'display_skill': x.get('INCLUSION_IND') or 'None Listed',
            'update_user_id': x.get('JCS_LAST_UPDT_USER_ID') or 'None Listed',
            'update_date': x.get('JCS_LAST_UPDT_TMSMP_DT') or 'None Listed'
        }
    return list(map(jc_skills_results_mapping, data.get('QRY_LSTSKILLS_REF')))

def save_new_cat_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Save New Job Category failed.")
        return None

    return data

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

def map_new_category_query(req):
    mapped_request = {
      "PV_API_VERSION_I": "", 
      "PV_AD_ID_I": "",
      "I_JC_NM_TXT": req.get('category_name'),
      "I_SKILL_CODE": req.get('skill_codes'),
    }

    return mapped_request