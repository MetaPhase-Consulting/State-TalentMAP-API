import logging
from talentmap_api.fsbid.services import common as services, employee

logger = logging.getLogger(__name__)

def get_job_categories_data(jwt_token, request):
    '''
    Gets a list of all Job Categories
    '''
    args = {
        "proc_name": 'qry_lstJobCats',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": {},
        "request_mapping_function": job_categories_req_mapping,
        "response_mapping_function": job_categories_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def job_categories_req_mapping(req):
    mapped_request = {
      "PV_API_VERSION_I": "",
      "PV_AD_ID_I": "",
      "QRY_LSTJOBCATS_REF": "",
    }

    return mapped_request

def job_categories_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Job Categories failed.")
        return None

    def jc_results_mapping(x):
        return {
            'id': x.get('JC_ID') or '-',
            'description': x.get('JC_NM_TXT') or 'None Listed',
        }
    return list(map(jc_results_mapping, data.get('QRY_LSTJOBCATS_REF')))


def get_job_category_skills(jwt_token, request):
    '''
    Returns all Skills with an indicator field set to 1 on those
    Skills which are associated with the Job Category
    '''
    args = {
        "proc_name": 'qry_getJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": jc_skills_req_mapping,
        "response_mapping_function": jc_skills_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def jc_skills_req_mapping(req):
    mapped_request = {
      "PV_API_VERSION_I": "",
      "PV_AD_ID_I": "",
      "I_JC_ID": req.get('category_id'),
    }

    return mapped_request

def jc_skills_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Job Categories Skills failed.")
        return None

    def jc_skills_results_mapping(x):
        return {
            'code': x.get('SKL_CODE') or '-',
            'description': x.get('SKL_DESC') or 'None Listed',
            'display_skill': x.get('INCLUSION_IND') or 'None Listed',
            'update_user_id': x.get('JCS_LAST_UPDT_USER_ID') or 'None Listed',
            'update_date': x.get('JCS_LAST_UPDT_TMSMP_DT') or 'None Listed'
        }
    return list(map(jc_skills_results_mapping, data.get('QRY_LSTSKILLS_REF')))

