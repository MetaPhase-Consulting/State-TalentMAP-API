import logging
import requests  # pylint: disable=unused-import
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response


logger = logging.getLogger(__name__)

# ======================== Get PV Filters ========================

def get_admin_projected_vacancy_filters(jwt_token):
    '''
    Gets Filters for Admin Projected Vacancies
    '''
    args = {
        "proc_name": "PRC_FV_ADMIN_SEARCH",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_body": {},
        "request_mapping_function": admin_projected_vacancy_filter_request_mapping,
        "response_mapping_function": admin_projected_vacancy_filter_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_filter_request_mapping(request):
    return {
        "PV_API_VERSION_I": '',
        "PV_AD_ID_I": '',
    }

def admin_projected_vacancy_filter_response_mapping(response):
    def bureau_map(x):
        return {
            'code': x.get('BUREAU_ORG_CODE'),
            'short_description': x.get('BUREAU_SHORT_DESC'),
            'description': x.get('BUREAU_LONG_DESC'),
        }
    def organization_map(x):
        return {
            'code': x.get('ORG_CODE'),
            'short_description': x.get('ORG_SHORT_DESC'),
            'description': x.get('ORG_LONG_DESC'),
        }
    def grade_map(x):
        return {
            'code': x.get('GRD_GRADE_CODE'),
            'description': x.get('GRD_GRADE_CODE'),
        }
    def skill_map(x):
        return {
            'code': x.get('SKL_CODE'),
            'description': x.get('SKL_DESC'),
        }
    def language_map(x):
        return {
            'code': x.get('LANG_CODE'),
            'short_description': x.get('LANG_SHORT_DESC'),
            'description': x.get('LANG_LONG_DESC'),
        }
    def bid_season_map(x):
        return {
            'code': x.get('BSN_ID'),
            'description': x.get('BSN_DESCR_TEXT'),
            'start_date': x.get('BSN_START_DATE'),
            'end_date': x.get('BSN_END_DATE'),
            'panel_cutoff_date': x.get('BSN_PANEL_CUTOFF_DATE'),
            'future_vacancy_indicator': x.get('BSN_FUTURE_VACANCY_IND'),
        }
    def status_map(x):
        return {
            'code': x.get('FVS_CODE'),
            'description': x.get('FVS_DESCR_TXT'),
        }
    return {
        'bureauFilters': list(map(bureau_map, response.get('PCUR_BUREAU_TAB_O'))),
        'organizationFilters': list(map(organization_map, response.get('PCUR_ORG_TAB_O'))),
        'gradeFilters': list(map(grade_map, response.get('PCUR_GRADE_TAB_O'))),
        'skillFilters': list(map(skill_map, response.get('PCUR_SKILL_TAB_O'))),
        'languageFilters': list(map(language_map, response.get('PCUR_LANGUAGE_TAB_O'))),
        'bidSeasonFilters': list(map(bid_season_map, response.get('PCUR_BSN_TAB_O'))),
        'futureVacancyStatusFilters': list(map(status_map, response.get('PCUR_FVS_TAB_O'))),
    }

# ======================== Get PV Dropdowns ========================

def get_admin_projected_vacancy_language_offsets(jwt_token):
    '''
    Gets Language Offsets for Admin Projected Vacancies
    '''
    args = {
        "proc_name": "PRC_LST_POS_PLO_CRITERIA",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_body": {},
        "request_mapping_function": admin_projected_vacancy_filter_request_mapping,
        "response_mapping_function": admin_projected_vacancy_language_offsets_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_language_offsets_response_mapping(response):
    def language_offsets_map(x):
        return {
            'code': x.get("LOT_SEQ_NUM"),
            'description': x.get("LO_DESCR_TEXT"),
        }
    return {
        'summerLanguageOffsetFilters': list(map(language_offsets_map, response.get("PQRY_LANG_OFFSET_S_O"))),
        'winterLanguageOffsetFilters': list(map(language_offsets_map, response.get("PQRY_LANG_OFFSET_W_O"))),
    }

# ======================== Get PV List ========================

def get_admin_projected_vacancies(query, jwt_token):
    '''
    Gets List Data for Admin Projected Vacancies 
    '''
    args = {
        "proc_name": "prc_lst_fv_admin",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_body": query,
        "request_mapping_function": admin_projected_vacancy_request_mapping,
        "response_mapping_function": admin_projected_vacancy_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_request_mapping(request):
    mapped_request = {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
    }
    if request.get('bureaus'):
        mapped_request['PJSON_BUREAU_TAB_I'] = services.format_request_data_to_string(request.get('bureaus'), 'BUREAU_ORG_CODE')
    if request.get('organizations'):
        mapped_request['PJSON_ORG_TAB_I'] = services.format_request_data_to_string(request.get('organizations'), 'ORG_CODE')
    if request.get('bidSeasons'):
        mapped_request['PJSON_BSN_TAB_I'] = services.format_request_data_to_string(request.get('bidSeasons'), 'BSN_ID')
    if request.get('grades'):
        mapped_request['PJSON_GRADE_TAB_I'] = services.format_request_data_to_string(request.get('grades'), 'GRD_GRADE_CODE')
    if request.get('skills'):
       mapped_request['PJSON_SKILL_TAB_I'] = services.format_request_data_to_string(request.get('skills'), 'SKL_CODE')
    if request.get('languages'):
        mapped_request['PJSON_LANGUAGE_TAB_I'] = services.format_request_data_to_string(request.get('languages'), 'LANG_CODE')
    return mapped_request

def admin_projected_vacancy_response_mapping(response):
    def projected_vacancy_mapping(x):
        return {
            "bid_season_code": x.get("BSN_ID"),
            "bid_season_description": x.get("BSN_DESCR_TEXT"),
            "bureau_code": x.get("BUREAU_CODE"),
            "bureau_short_description": x.get("BUREAU_SHORT_DESC"),
            "bureau_description": x.get("BUREAU_LONG_DESC"),
            "organization_code": x.get("ORG_CODE"),
            "organization_short_description": x.get("ORG_SHORT_DESC"),
            "organization_description": x.get("ORG_LONG_DESC"),
            "positon_seq_num": x.get("POS_SEQ_NUM"),
            "position_title": x.get("POS_TITLE_DESC"),
            "position_number": x.get("POS_NUM_TEXT"),
            "position_pay_plan_code": x.get("POS_PAY_PLAN_CODE"),
            "position_grade_code": x.get("POS_GRADE_CODE"),
            "position_skill_code": x.get("POS_SKILL_CODE"),
            "position_skill_description": x.get("POS_SKILL_DESC"),
            "position_job_category_code": x.get("POS_JOBCAT_CODE"),
            "position_job_category_description": x.get("POS_JOBCAT_DESC"),
            "positon_language1_code": x.get("POS_LANGUAGE_1_CODE"),
            "positon_language2_code": x.get("POS_LANGUAGE_2_CODE"),
            "position_language_profficiency_code": x.get("POS_POSITION_LANG_PROF_CODE"),
            "position_language_profficiency_description": x.get("POS_POSITION_LANG_PROF_DESC"),
            "future_vacancy_seq_num": x.get("FV_SEQ_NUM"),
            "future_vacancy_seq_num_ref": x.get("FV_SEQ_NUM_REF"),
            "future_vacancy_override_code": x.get("FVO_CODE"),
            "future_vacancy_override_description": x.get("FVO_DESCR_TXT"),
            "future_vacancy_comment": x.get("FV_COMMENT_TXT"),
            "future_vacancy_override_tour_end_date": x.get("FV_OVERRIDE_TED_DATE"),
            "future_vacancy_system_indicator": x.get("FV_SYSTEM_IND"),
            "future_vacancy_status_code": x.get("FVS_CODE"),
            "future_vacancy_status_description": x.get("FVS_DESCR_TXT"),
            "future_vacancy_mc_indicator": x.get("FV_MC_IND"),
            "future_vacancy_exclude_import_indicator": x.get("FV_EXCL_IMPORT_IND"),
            "assignment_seq_num": x.get("ASG_SEQ_NUM"),
            "assignment_seq_num_effective": x.get("ASG_SEQ_NUM_EF"),
            "assignee_tour_end_date": x.get("ASSIGNEE_TED"),
            "assignee": x.get("ASSIGNEE"),
            "incumbent": x.get("INCUMBENT"),
            "cycle_date_type_code": x.get("CDT_CD"),
            "assignment_status_code": x.get("ASGS_CODE"),
            "bidding_tool_differential_rate_number": x.get("BT_DIFFERENTIAL_RATE_NUM"),
            "bidding_tool_danger_rate_number": x.get("BT_DANGER_PAY_NUM"),
            "bidding_tool_most_difficult_to_staff_flag": x.get("BT_MOST_DIFFICULT_TO_STAFF_FLG"),
            "bidding_tool_service_need_differential_flag": x.get("BT_SERVICE_NEEDS_DIFF_FLG"),
            "tour_of_duty_code": x.get("TOD_CODE"),
            "tour_of_duty_description": x.get("TOD_DESC_TEXT"),
            "unaccompanied_status_code": x.get("US_CODE"),
            "unaccompanied_status_description": x.get("US_DESC_TEXT"),
            "position_overseas_indicator": x.get("POS_OVERSEAS_IND"),
            "state_country_code": x.get("STATECOUNTRYCODE"),
            "state_country_description": x.get("STATECOUNTRYNAME"),
            "contact_name": x.get("CONTACT_NAME"),
            "entry_level_indicator": x.get("EL_IND"),
            "midlevel_cede_indicator": x.get("ML_CEDE_IND"),
            "location_code": x.get("LOCATION_CODE"),
            "location_description": x.get("LOCATION_DESC"),
            "commuter_code": x.get("COMMUTER_CODE"),
            "commuter_description": x.get("COMMUTER_DESC"),
            "alternate_bureau_code": x.get("ALT_BUREAU_CODE"),
            "alternate_bureau_description": x.get("ALT_BUREAU_SHORT_DESC"),
            "capsule_description": x.get("CAPSULE_DESC"),
            "capsule_position_description": x.get("CAPSULE_POSITION_DESC"),
            "famer_link": x.get("FAMER_LINK"),
            "bidding_tool": x.get("BIDDING_TOOL"),
            "cycle_position_link": x.get("CP_LINK"),
            "bid_season_future_vacancy_indicator": x.get("BSN_FUTURE_VACANCY_IND"),
            "cycle_position_id": x.get("CP_ID"),
        }
    return list(map(projected_vacancy_mapping, response.get("PQRY_FV_ADMIN_O")))

# ======================== Edit PV ========================

def edit_admin_projected_vacancy(data, jwt_token):
    '''
    Edit Admin Projected Vacancy
    '''
    args = {
        "proc_name": 'PRC_IUD_FUTURE_VACANCY',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": edit_admin_projected_vacancy_request_mapping,
        "response_mapping_function": edit_admin_projected_vacancy_response_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_admin_projected_vacancy_request_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'pv_action_i': 'U',
        'pjson_fv_i': {
            'Data': [{
                'FV_SEQ_NUM': request.get('future_vacancy_seq_num'),
                'FV_SEQ_NUM_REF': request.get('future_vacancy_seq_num_ref'),
                'POS_SEQ_NUM': request.get('positon_seq_num'),
                'BSN_ID': request.get('bid_season_code'),
                'ASG_SEQ_NUM_EF': request.get('assignment_seq_num_effective'),
                'ASG_SEQ_NUM': request.get('assignment_seq_num'),
                'CDT_CD': request.get('cycle_date_type_code'),
                'FVS_CODE': request.get('future_vacancy_status_code'),
                'FVO_CODE': request.get('future_vacancy_override_code'),
                'FV_OVERRIDE_TED_DATE': request.get('future_vacancy_override_tour_end_date'),
                'FV_SYSTEM_IND': request.get('future_vacancy_system_indicator'),
                'FV_COMMENT_TXT': request.get('future_vacancy_comment'),
                'FV_CREATE_ID': request.get('created_date'),
                'FV_CREATE_DATE': request.get('creator_id'),
                'FV_UPDATE_ID': request.get('updater_id'),
                'FV_UPDATE_DATE': request.get('updated_date'),
                'FV_MC_IND': request.get('future_vacancy_mc_indicator'),
                'FV_EXCL_IMPORT_IND': request.get('future_vacancy_exclude_import_indicator'),
            }]
        }
    }

def edit_admin_projected_vacancy_response_mapping(data):
    return service_response(data, 'Projected Vacancy Edit')