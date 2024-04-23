from django.conf import settings
from datetime import datetime as dt
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response

WS_ROOT = settings.WS_ROOT_API_URL


def get_bid_audit_data(jwt_token, request):
    '''
    Gets the Data for the Bid Audit Page
    '''
    args = {
        "proc_name": 'qry_lstauditassigncycles',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_body": request,
        "request_mapping_function": get_bid_audit_req_mapping,
        "response_mapping_function": get_bid_audit_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_bid_audit_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }
    return mapped_request


def format_dates(input_date):
    if input_date == '' or input_date is None:
        return input_date
    date_object = dt.strptime(input_date, "%Y-%m-%dT%H:%M:%S")
    formatted_date = date_object.strftime("%m/%d/%Y")
    return formatted_date

def get_bid_audit_res_mapping(data):
    def results_mapping(x):
        return {
            'audit_id': x.get('AAC_AUDIT_NBR') or None,
            'audit_desc': x.get('AAC_DESC_TXT') or None,
            'audit_date': format_dates(x.get('AAC_AUDIT_DT')) if x.get('AAC_AUDIT_DT') else None,
            'audit_date_unformatted': x.get('AAC_AUDIT_DT'),
            'posted_by_date': format_dates(x.get('AAC_POSTED_BY_DT')) if x.get('AAC_POSTED_BY_DT') else None,
            'cycle_id': x.get('CYCLE_ID') or None,
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'cycle_status_code': x.get('CS_CD') or None,
            'cycle_status': x.get('CS_DESCR_TXT') or None,
            'cycle_category_code': x.get('CC_CD') or None,
            'cycle_category': x.get('CC_DESCR_TXT') or None,
        }

    def sort_by_audit_date(audits):
        if audits['audit_date_unformatted'] is None:
            return ''
        else:
            return audits['audit_date_unformatted']

    def success_mapping(x):
        audits = list(map(results_mapping, x.get('QRY_LSTAUDITASSIGNCYCLES_REF', {})))
        sorted_audits = sorted(audits, key=sort_by_audit_date, reverse=True)
        return sorted_audits

    return service_response(data, 'Bid Audit Get Audits', success_mapping)


def get_in_category(jwt_token, request):
    '''
    Gets In Category Positions for a Cycle
    '''
    args = {
        "proc_name": 'qry_lstauditincategories',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_body": request,
        "request_mapping_function": get_in_category_req_mapping,
        "response_mapping_function": get_in_category_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_in_category_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditId'),
    }
    return mapped_request


def get_in_category_res_mapping(data):
    def in_category_results_mapping(x):
        return {
            'id': x.get('AIC_ID') or None,
            'skill_code_position': x.get('SKL_CODE_POS') or None,
            'skill_desc_position': x.get('skl_desc_pos') or None,
            'skill_code_employee': x.get('SKL_CODE_EMP') or None,
            'skill_desc_employee': x.get('skl_desc_emp') or None,
        }

    def success_mapping(x):
        return list(map(in_category_results_mapping, x.get('QRY_LSTAUDITINCATEGORIES_REF', {})))

    return service_response(data, 'Bid Audit Get Audits', success_mapping)


def get_at_grade(jwt_token, request):
    '''
    Gets In Category Positions for a Cycle
    '''
    args = {
        "proc_name": 'qry_lstauditatgrades',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_body": request,
        "request_mapping_function": get_at_grade_req_mapping,
        "response_mapping_function": get_at_grade_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_at_grade_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditId'),
    }
    return mapped_request


def get_at_grade_res_mapping(data):
    def in_category_results_mapping(x):
        return {
            'id': x.get('AAG_ID') or None,
            'grade_code_position': x.get('GRD_CODE_POS') or None,
            'skill_code_position': x.get('SKL_CODE_POS') or None,
            'skill_desc_position': x.get('skl_desc_pos') or None,
            'grade_code_employee': x.get('GRD_CODE_EMP') or None,
            'skill_code_employee': x.get('SKL_CODE_EMP') or None,
            'skill_desc_employee': x.get('skl_desc_emp') or None,
            'tenure_code_employee': x.get('TNR_CODE_EMP') or None,
            'tenure_desc_employee': x.get('tnr_desc_emp') or None,
        }

    def success_mapping(x):
        return list(map(in_category_results_mapping, x.get('QRY_LSTAUDITATGRADES_REF', {})))

    return service_response(data, 'Bid Audit Get Audits', success_mapping)
