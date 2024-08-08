from django.conf import settings
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response, format_dates

WS_ROOT = settings.WS_ROOT_API_URL


def run_bid_audit(jwt_token, request):
    '''
    Runs the Bid Audit
    '''
    args = {
        "proc_name": 'act_runauditassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": run_bid_audit_req_mapping,
        "response_mapping_function": run_bid_audit_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def run_bid_audit_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_aac_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
    }
    return mapped_request


def run_bid_audit_res_mapping(data):
    return service_response(data, 'Run Bid Audit')


def get_bid_audit_data(jwt_token, request):
    '''
    Gets the Data for the Bid Audit Page
    '''
    args = {
        "proc_name": 'qry_lstauditassigncycles',
        "package_name": 'PKG_WEBAPI_WRAP',
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



def get_bid_audit_res_mapping(data):
    def results_mapping(x):
        return {
            'audit_id': x.get('AAC_AUDIT_NBR') or None,
            'audit_desc': x.get('AAC_DESC_TXT') or None,
            'audit_date': format_dates(x.get('AAC_AUDIT_DT')) if x.get('AAC_AUDIT_DT') else None,
            'posted_by_date': format_dates(x.get('AAC_POSTED_BY_DT')) if x.get('AAC_POSTED_BY_DT') else None,
            'cycle_id': x.get('CYCLE_ID') or None,
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'cycle_status_code': x.get('CS_CD') or None,
            'cycle_status': x.get('CS_DESCR_TXT') or None,
            'cycle_category_code': x.get('CC_CD') or None,
            'cycle_category': x.get('CC_DESCR_TXT') or None,
        }

    def success_mapping(x):
        audits = list(map(results_mapping, x.get('QRY_LSTAUDITASSIGNCYCLES_REF', {})))
        sorted_audits = sorted(audits, key=lambda x: (x['cycle_id'], x['audit_id']), reverse=True)
        return sorted_audits

    return service_response(data, 'Bid Audit Get Audits', success_mapping)


def get_cycles(jwt_token, request):
    '''
    Get Active Cycles for New Bid Audits
    '''
    args = {
        "proc_name": 'qry_addauditassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": get_bid_audit_req_mapping,
        "response_mapping_function": get_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_cycles_res_mapping(data):
    def results_mapping(x):
        return {
            'id': x.get('CYCLE_ID') or None,
            'name': x.get('CYCLE_NM_TXT') or None,
            'audit_number': x.get('aac_audit_nbr'),
        }

    def success_mapping(x):
        return list(map(results_mapping, x.get('QRY_ADDAUDITASSIGNCYCLE_REF', {})))

    return service_response(data, 'Bid Audit Get Cycles', success_mapping)


def create_new_audit(jwt_token, request):
    '''
    Create a new Bid Audit
    '''
    args = {
        "proc_name": 'act_addauditassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": create_new_audit_req_mapping,
        "response_mapping_function": create_new_audit_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def create_new_audit_req_mapping(request):
    cycle_id = request.get('id')
    audit_number = request.get('auditNumber')
    audit_desc = request.get('auditDescription')
    posted_by_date = request.get('postByDate')

    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': cycle_id,
        'i_aac_desc_txt': audit_desc,
        'i_aac_audit_nbr': audit_number,
        'i_aac_posted_by_dt': posted_by_date,
    }

    return mapped_request


def create_new_audit_res_mapping(data):
    return service_response(data, 'Save Bid Audit')


def update_bid_audit(jwt_token, request):
    '''
    Update a Bid Audit
    '''
    args = {
        "proc_name": 'act_modauditassigncycle',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": create_new_audit_req_mapping,
        "response_mapping_function": create_new_audit_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_bid_count(jwt_token, request):
    '''
    Run Bid Audit, Updates Bid Count
    '''
    args = {
        "proc_name": 'act_runauditdynamic',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": get_bid_audit_req_mapping,
        "response_mapping_function": update_bid_count_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_bid_count_res_mapping(data):
    return service_response(data, 'Update Bid Counts')


def get_in_category(jwt_token, request):
    '''
    Gets In Category Positions for a Cycle
    '''
    args = {
        "proc_name": 'qry_lstauditincategories',
        "package_name": 'PKG_WEBAPI_WRAP',
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
            'position_skill_code': x.get('SKL_CODE_POS') or None,
            'position_skill_desc': x.get('skl_desc_pos') or None,
            'employee_skill_code': x.get('SKL_CODE_EMP') or None,
            'employee_skill_desc': x.get('skl_desc_emp') or None,
        }

    def in_category_audit_mapping(x):
        return {
            'cycle_id': x.get('CYCLE_ID') or None,
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'audit_date': format_dates(x.get('AAC_AUDIT_DT')) if x.get('AAC_AUDIT_DT') else None,
            'audit_number': x.get('AAC_AUDIT_NBR') or None,
            'audit_desc': x.get('AAC_DESC_TXT') or None,
            'last_updated': x.get('AAC_LAST_UPDT_TMSMP_DT') or None,
            'last_updated_id': x.get('AAC_LAST_UPDT_USER_ID') or None,
            'posted_by_date': format_dates(x.get('AAC_POSTED_BY_DT')) if x.get('AAC_POSTED_BY_DT') else None,
        }

    def success_mapping(x):
        results = {
            "in_categories": list(map(in_category_results_mapping, x.get('QRY_LSTAUDITINCATEGORIES_REF', {}))),
            "audit_info": in_category_audit_mapping(x['QRY_GETAUDITASSIGNCYCLE_REF'][0]),
        }
        return results

    return service_response(data, 'Bid Audit Get In-Category', success_mapping)


def get_at_grade(jwt_token, request):
    '''
    Gets In Category Positions for a Cycle
    '''
    args = {
        "proc_name": 'qry_lstauditatgrades',
        "package_name": 'PKG_WEBAPI_WRAP',
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
            'position_grade_code': x.get('GRD_CODE_POS') or None,
            'position_skill_code': x.get('SKL_CODE_POS') or None,
            'position_skill_desc': x.get('skl_desc_pos') or None,
            'employee_grade_code': x.get('GRD_CODE_EMP') or None,
            'employee_skill_code': x.get('SKL_CODE_EMP') or None,
            'employee_skill_desc': x.get('skl_desc_emp') or None,
            'employee_tenure_code': x.get('TNR_CODE_EMP') or None,
            'employee_tenure_desc': x.get('tnr_desc_emp') or None,
        }

    def at_grade_audit_mapping(x):
        return {
            'cycle_id': x.get('CYCLE_ID') or None,
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'audit_date': format_dates(x.get('AAC_AUDIT_DT')) if x.get('AAC_AUDIT_DT') else None,
            'audit_number': x.get('AAC_AUDIT_NBR') or None,
            'audit_desc': x.get('AAC_DESC_TXT') or None,
            'last_updated': x.get('AAC_LAST_UPDT_TMSMP_DT') or None,
            'last_updated_id': x.get('AAC_LAST_UPDT_USER_ID') or None,
            'posted_by_date': format_dates(x.get('AAC_POSTED_BY_DT')) if x.get('AAC_POSTED_BY_DT') else None,
        }

    def success_mapping(x):
        results = {
            "at_grades": list(map(in_category_results_mapping, x.get('QRY_LSTAUDITATGRADES_REF', {}))),
            "audit_info": at_grade_audit_mapping(x['QRY_GETAUDITASSIGNCYCLE_REF'][0]),
        }
        return results

    return service_response(data, 'Bid Audit Get At-Grade', success_mapping)


def get_in_category_options(jwt_token, request):
    '''
    Gets In Category Options for Positions
    '''
    args = {
        "proc_name": 'qry_addauditincategory',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": get_in_category_req_mapping,
        "response_mapping_function": get_in_category_options_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_in_category_options_res_mapping(data):
    def in_category_options_mapping(x):
        return {
            'code': x.get('SKL_CODE') or None,
            'text': x.get('SKL_DESC') or None,
        }

    def success_mapping(x):
        results = {
            'position_skill_options': list(map(in_category_options_mapping, x.get('QRY_LSTAUDITPOSSKILLS_REF', {}))),
            'employee_skill_options': list(map(in_category_options_mapping, x.get('QRY_LSTAUDITEMPSKILLS_REF', {})))
        }
        return results

    return service_response(data, 'Bid Audit Get In-Category', success_mapping)


def create_new_in_category(jwt_token, request):
    '''
    Create In Category Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_addauditincategory',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": create_in_category_req_mapping,
        "response_mapping_function": create_in_category_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def create_in_category_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_skl_code_pos': request.get('positionSkill'),
        'i_skl_code_emp': request.get('employeeSkill'),
    }
    return mapped_request


def create_in_category_res_mapping(data):
    return service_response(data, 'Save In Category')


def get_at_grade_options(jwt_token, request):
    '''
    Gets At Grade Options for Positions
    '''
    args = {
        "proc_name": 'qry_addauditatgrade',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": get_at_grade_req_mapping,
        "response_mapping_function": get_at_grade_options_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_at_grade_options_res_mapping(data):
    def at_grade_grade_options_mapping(x):
        return {
            'code': x.get('GRD_CD'),
        }

    def at_grade_skill_options_mapping(x):
        return {
            'code': x.get('SKL_CODE'),
            'text': x.get('SKL_DESC'),
        }

    def at_grade_tenure_options_mapping(x):
        return {
            'code': x.get('TNR_CODE'),
            'text': x.get('TNR_DESC'),
        }

    def success_mapping(x):
        results = {
            'position_grade_options': list(map(at_grade_grade_options_mapping, x.get('QRY_LSTAUDITPOSGRADES_REF', {}))),
            'position_skill_options': list(map(at_grade_skill_options_mapping, x.get('QRY_LSTAUDITPOSSKILLS_REF', {}))),
            'employee_grade_options': list(map(at_grade_grade_options_mapping, x.get('QRY_LSTAUDITEMPGRADES_REF', {}))),
            'employee_skill_options': list(map(at_grade_skill_options_mapping, x.get('QRY_LSTAUDITEMPSKILLS_REF', {}))),
            'employee_tenure_options': list(map(at_grade_tenure_options_mapping, x.get('QRY_LSTAUDITEMPTENURES_REF', {}))),
        }
        return results

    return service_response(data, 'Bid Audit Get At-Grade', success_mapping)


def create_new_at_grade(jwt_token, request):
    '''
    Create At Grade Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_addauditatgrade',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": create_at_grade_req_mapping,
        "response_mapping_function": create_at_grade_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def create_at_grade_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_skl_code_pos': request.get('positionSkill'),
        'i_grd_code_pos': request.get('positionGrade'),
        'i_grd_code_emp': request.get('employeeGrade'),
        'i_skl_code_emp': request.get('employeeSkill'),
        'i_tnr_code_emp': request.get('employeeTenure'),
    }
    return mapped_request


def create_at_grade_res_mapping(data):
    return service_response(data, 'Save At Grade')


def update_at_grade(jwt_token, request):
    '''
    Update At Grade Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_modauditatgrade',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": update_at_grade_req_mapping,
        "response_mapping_function": update_at_grade_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_at_grade_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_aag_id': request.get('auditGradeId'),
        'i_skl_code_pos': request.get('posSkillCode'),
        'i_grd_code_pos': request.get('posGradeCode'),
        'i_grd_code_emp': request.get('empGradeCode'),
        'i_skl_code_emp': request.get('empSkillCode'),
        'i_tnr_code_emp': request.get('empTenCode'),
    }
    return mapped_request


def update_at_grade_res_mapping(data):
    return service_response(data, 'Update At Grade')


def update_in_category(jwt_token, request):
    '''
    Update In Category Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_modauditincategory',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": update_in_category_req_mapping,
        "response_mapping_function": update_in_category_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def update_in_category_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_aic_id': request.get('auditCategoryId'),
        'i_skl_code_pos': request.get('posCode'),
        'i_skl_code_emp': request.get('empCode'),
    }
    return mapped_request


def update_in_category_res_mapping(data):
    return service_response(data, 'Update In Category')


def delete_at_grade(jwt_token, request):
    '''
    delete At Grade Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_delauditatgrade',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": delete_at_grade_req_mapping,
        "response_mapping_function": delete_at_grade_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def delete_at_grade_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_aag_id': request.get('auditGradeId'),
    }
    return mapped_request


def delete_at_grade_res_mapping(data):
    return service_response(data, 'Delete At Grade')


def delete_in_category(jwt_token, request):
    '''
    delete In Category Relationships for Cycle Positions
    '''
    args = {
        "proc_name": 'act_delauditincategory',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_body": request,
        "request_mapping_function": delete_in_category_req_mapping,
        "response_mapping_function": delete_in_category_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def delete_in_category_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditNbr'),
        'i_aic_id': request.get('auditCategoryId'),
    }
    return mapped_request


def delete_in_category_res_mapping(data):
    return service_response(data, 'Delete In Category')


def get_audited_data(jwt_token, request):
    '''
    Get Audit Data for a Specific bid Audit
    '''
    args = {
        "proc_name": 'qry_lstBidBook',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_body": request,
        "request_mapping_function": get_audit_data_req_mapping,
        "response_mapping_function": get_audit_data_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def get_audit_data_req_mapping(request):
    # return all of the bidding data by passing in every grade code
    # since we are not using a search page to fetch more specific data
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_grd_cd': '00,01,02,03,04,05,06,07,MC,OC,OM',
        'i_cycle_id': request.get('cycleId'),
        'i_aac_audit_nbr': request.get('auditId'),
    }
    return mapped_request


def get_audit_data_res_mapping(data):
    def results_mapping(x):
        return {
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'org_short_desc': x.get('ORGS_SHORT_DESC') or None,
            'org_code': x.get('ORG_CODE') or None,
            'position_number': x.get('POS_NUM_TXT') or None,
            'position_title': x.get('POS_PTITLE') or None,
            'position_grade': x.get('POS_GRD_CD') or None,
            'position_skill': x.get('POS_SKL_CODE_POS') or None,
            'position_lang': x.get('POSLTEXT') or None,
            'position_incumbent_name': x.get('POS_INCUMBENT_NAME') or None,
            'position_incumbent_ted': x.get('ACP_INCUMBENT_TED') or None,
            'audit_cycle_position_id': x.get('ACP_ID') or None,
            'count_total_bidders': x.get('ACP_TTL_BIDDER_QTY') or None,
            'count_at_grade': x.get('ACP_AT_GRD_QTY') or None,
            'count_in_category': x.get('ACP_IN_CATEGORY_QTY') or None,
            'count_at_grade_in_category': x.get('ACP_AT_GRD_IN_CATEGORY_QTY') or None,
            'count_total_group_members': x.get('ACP_TTL_GROUP_MEMBERS_QTY') or None,
            'hard_to_fill_ind': x.get('ACP_HARD_TO_FILL_IND') or None,
            'bidder_name': x.get('BIDDER_FULL_NAME') or None,
            'bidder_org_desc': x.get('BIDDER_ORG_SHORT_DESC') or None,
            'bidder_position_number': x.get('BIDDER_POS_NUM_TXT') or None,
            'bidder_position_title': x.get('BIDDER_PTITLE') or None,
            'bidder_grade': x.get('BIDDER_GRADE_CODE') or None,
            'bidder_skill': x.get('BIDDER_SKL_1_CODE') or None,
            'bidder_lang': x.get('BIDDER_EMPLTEXT') or None,
            'bidder_ted': x.get('BIDDER_TED_DT') or None,
            'bidder_is_at_grade': x.get('BIDDER_AT_GRADE_IND') or None,
            'bidder_is_in_category': x.get('BIDDER_IN_CATEGORY_IND') or None,
            'bidder_cats': x.get('BIDDER_CATS') or None,
            'ae_stretch_ind': x.get('AE_STRETCH_IND') or None,
        }

    def reference_mapping(x):
        return {
            'cycle_id': x.get('CYCLE_ID') or None,
            'cycle_name': x.get('CYCLE_NM_TXT') or None,
            'audit_number': x.get('AAC_AUDIT_NBR') or None,
            'audit_desc': x.get('AAC_DESC_TXT') or None,
            'audit_posted_by_date': x.get('AAC_POSTED_BY_DT') or None,
            'audit_date': x.get('AAC_AUDIT_DT') or None,
            'prev_audit_number': x.get('PREV_NBR') or None,
            'next_audit_number': x.get('NEXT_NBR') or None,
            'cycle_category': x.get('CC_CD') or None,
        }

    def success_mapping(x):
        results = {
            'audit_data': list(map(results_mapping, x.get('QRY_LSTBIDBOOK_REF', {}))),
            'ref_data': reference_mapping(x['QRY_GETCYCLE_REF'][0]),
        }
        return results

    return service_response(data, 'Bid Audit Get Audits', success_mapping)
