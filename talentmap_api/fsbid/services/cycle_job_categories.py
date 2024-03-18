import logging
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response


logger = logging.getLogger(__name__)

# ======================== Get Cycle Categories ========================

def get_cycle_categories(pk, jwt_token):
    '''
    Gets Cycle Categories
    '''
    args = {
        "proc_name": "qry_lstcyclejobs",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT100",
        "request_body": pk,
        "request_mapping_function": cycle_categories_req_mapping,
        "response_mapping_function": cycle_categories_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def cycle_categories_req_mapping(request):
    return {
        "PV_API_VERSION_I": '',
        "PV_AD_ID_I": '',
    }

def cycle_categories_res_mapping(response):
    def categories(x):
        return {
            'code': x.get('CC_CD'),
            'description': x.get('CC_DESCR_TXT'),
        }
    def success_mapping(x):
        return list(map(categories, x.get('QRY_LSTCYCLES_REF')))
    return service_response(response, 'Cycle Categories List Data', success_mapping)

# ======================== Get Cycle Job Categories ========================

def get_cycle_job_categories(pk, jwt_token):
    '''
    Gets Cycle Job Categories for a Cycle Category
    '''
    args = {
        "proc_name": "qry_getcyclejob",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT100",
        "request_body": pk,
        "request_mapping_function": cycle_job_categories_req_mapping,
        "response_mapping_function": cycle_job_categories_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def cycle_job_categories_req_mapping(request):
    return {
        "PV_API_VERSION_I": '',
        "PV_AD_ID_I": '',
        "i_cc_cd": request,
    }

def cycle_job_categories_res_mapping(response):
    def categories(x):
        return {
            'code': x.get('JC_ID'),
            'description': x.get('JC_NM_TXT'),
            'updater_id': x.get('CJC_LAST_UPDT_USER_ID'),
            'updated_date': x.get('CJC_LAST_UPDT_TMSMP_DT'),
            'included': x.get('INCLUSION_IND'),
        }
    def success_mapping(x):
        return list(map(categories, x.get('QRY_LSTJOBS_REF')))
    return service_response(response, 'Cycle Job Categories List Data', success_mapping)

# ======================== Edit Cycle Job Categories ========================

def edit_cycle_job_categories(data, jwt_token):
    '''
    Edit a Cycle Category's Cycle Job Category
    '''
    args = {
        "proc_name": 'act_modcyclejob',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": edit_cycle_job_categories_req_mapping,
        "response_mapping_function": edit_cycle_job_categories_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_cycle_job_categories_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "i_inclusion_ind": request.get('included'),
        "i_cc_cd": request.get('cycle_code'),
        "I_job_cat": request.get('job_codes'),
        "i_cjc_last_updt_tmsmp_dt": request.get('updated_dates'),
        "i_cjc_last_updt_user_id": request.get('updater_ids')
    }

def edit_cycle_job_categories_res_mapping(data):
    return service_response(data, 'Cycle Job Categories Edit')