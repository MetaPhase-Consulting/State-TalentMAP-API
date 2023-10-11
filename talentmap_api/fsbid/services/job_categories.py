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
            'display_skill': x.get('INCLUSION_IND') or '',
            'update_user_id': x.get('JCS_LAST_UPDT_USER_ID'),
            'update_date': x.get('JCS_LAST_UPDT_TMSMP_DT') or ''
        }
    job_category_info = {
        'status_ind': data.get('O_JC_STS_IND'),
        'update_date': data.get('O_JC_LAST_UPDT_TMSMP_DT'),
        'update_user_id': data.get('O_JC_LAST_UPDT_USER_ID')
    }
    return list((job_category_info, map(jc_skills_results_mapping, data.get('QRY_LSTSKILLS_REF'))))

def create_job_category(jwt_token, request):
    '''
    Saves a new Job Category with skills
    '''
    args = {
        "proc_name": 'act_addJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": create_jc_req_mapping,
        "response_mapping_function": create_jc_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def create_jc_req_mapping(req):
    mapped_request = {
      "PV_API_VERSION_I": "", 
      "PV_AD_ID_I": "",
      "I_JC_NM_TXT": req.get('category_name'),
      "I_SKILL_CODE": ','.join(req.get('skill_codes')),
    }
    logger.info('===mapped CREATE request===')
    logger.info(mapped_request)

    return mapped_request

def create_jc_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Save New Job Category failed.")
        return None

    return data

def edit_job_category(jwt_token, request):
    '''
    Updates a Job Category with user-selected skills
    '''
    args = {
        "proc_name": 'act_modJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": edit_jc_req_mapping,
        "response_mapping_function": edit_jc_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def edit_jc_req_mapping(req):
    mapped_request = {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_INCLUSION_IND": ','.join(req.get('inclusion_inds')),
        "I_JC_ID": req.get('category_id'),
        "I_JC_NM_TXT": req.get('category_name'),
        "I_JC_STS_IND": req.get('status_ind'),
        "I_JC_LAST_UPDT_TMSMP_DT": req.get('update_date'),
        "I_JC_LAST_UPDT_USER_ID": req.get('update_user_id'),
        "I_SKL_CODE": ','.join(req.get('skill_codes')),
        "I_JCS_LAST_UPDT_TMSMP_DT": ','.join(req.get('skill_update_dates')),
        "I_JCS_LAST_UPDT_USER_ID": ','.join(str(x) for x in req.get('skill_update_ids')),
        "O_RETURN_CODE": "",
        "QRY_ACTION_DATA": "",
        "QRY_ERROR_DATA": "",
    }
    logger.info('===mapped EDIT request===')
    logger.info(mapped_request)
    return mapped_request

def edit_jc_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Edit Job Category failed.")
        return None

    return data

def delete_job_category(jwt_token, request):
    '''
    Delete a Job Category
    '''
    args = {
        "proc_name": 'act_delJobCat',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "request_body": request,
        "request_mapping_function": delete_jc_req_mapping,
        "response_mapping_function": delete_jc_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def delete_jc_req_mapping(req):
    mapped_request = {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_JC_ID": req.get('category_id'),
        "I_JC_STS_IND": req.get('status_ind'),
        "I_JC_LAST_UPDT_TMSMP_DT": req.get('update_date'),
        "I_JC_LAST_UPDT_USER_ID": req.get('update_user_id'),
    }
    logger.info('===mapped DELETE request===')
    logger.info(mapped_request)

    return mapped_request

def delete_jc_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Delete Job Category failed.")
        return None

    return data