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
        "request_mapping_function": admin_projected_vacancy_filter_req_mapping,
        "response_mapping_function": admin_projected_vacancy_filter_res_mapping,
        "jwt_token": jwt_token,
        "request_body": {},
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_filter_req_mapping(request):
    return {
        "PV_API_VERSION_I": '',
        "PV_AD_ID_I": '',
    }

def admin_projected_vacancy_filter_res_mapping(response):
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
    def filters_map(x):
        return {
            'bureaus': list(map(bureau_map, x.get('PCUR_BUREAU_TAB_O'))),
            'organizations': list(map(organization_map, x.get('PCUR_ORG_TAB_O'))),
            'grades': list(map(grade_map, x.get('PCUR_GRADE_TAB_O'))),
            'skills': list(map(skill_map, x.get('PCUR_SKILL_TAB_O'))),
            'languages': list(map(language_map, x.get('PCUR_LANGUAGE_TAB_O'))),
            'bid_seasons': list(map(bid_season_map, x.get('PCUR_BSN_TAB_O'))),
            'statuses': list(map(status_map, x.get('PCUR_FVS_TAB_O'))),
        }
    return service_response(response, 'Projected Vacancy Filters', filters_map)

# ======================== Get PV Dropdowns ========================

def get_admin_projected_vacancy_language_offsets(jwt_token):
    '''
    Gets Language Offsets for Admin Projected Vacancies
    '''
    args = {
        "proc_name": "PRC_LST_POS_PLO_CRITERIA",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_mapping_function": admin_projected_vacancy_filter_req_mapping,
        "response_mapping_function": admin_projected_vacancy_language_offsets_res_mapping,
        "jwt_token": jwt_token,
        "request_body": {},
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_language_offsets_res_mapping(response):
    def language_offset_map(x):
        return {
            'code': x.get("LOT_SEQ_NUM"),
            'description': x.get("LO_DESCR_TEXT"),
        }
    def language_offsets_map(x):
        return {
            'summer_language_offsets': list(map(language_offset_map, x.get("PQRY_LANG_OFFSET_S_O"))),
            'winter_language_offsets': list(map(language_offset_map, x.get("PQRY_LANG_OFFSET_W_O"))),
        }
    return service_response(response, 'Projected Vacancy Language Offset Filters', language_offsets_map)

# ======================== Get PV List ========================

def get_admin_projected_vacancies(query, jwt_token):
    '''
    Gets List Data for Admin Projected Vacancies 
    '''
    args = {
        "proc_name": "prc_lst_fv_admin",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_mapping_function": admin_projected_vacancy_req_mapping,
        "response_mapping_function": admin_projected_vacancy_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_req_mapping(request):
    mapped_request = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PV_SUBTRAN_I': '',
        'PJSON_FVS_TAB_I': { 'Data': [] },
        'PJSON_CUST_TP_TAB_I': { 'Data': [] },
        'PXML_POSITION_I': '''
            <XMLSearchCriterias>
                <SearchList>
                    <Value>30008009</Value>
                    <Value>30008008</Value>
                </SearchList>
            </XMLSearchCriterias>
        ''',
        'PJSON_JC_DD_TAB_I': { 'Data': [] },
        'PXML_OVERSEAS_I': '''
            <XMLSearchCriterias>
                <SearchList>
                    <Value>O</Value>
                    <Value>D</Value>
                </SearchList>
            </XMLSearchCriterias>
        ''',
        'PQRY_FV_ADMIN_O': '',
        'PV_RETURN_CODE_O': '',
        'PQRY_ERROR_DATA_O': '',
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

def admin_projected_vacancy_res_mapping(response):
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
    def list_pv_mapping(x):
        return list(map(projected_vacancy_mapping, x.get("PQRY_FV_ADMIN_O")))
    return service_response(response, 'Projected Vacancy List', list_pv_mapping)

# ======================== Edit PV ========================

def edit_admin_projected_vacancy(data, jwt_token):
    '''
    Edit Admin Projected Vacancy
    '''
    args = {
        "proc_name": 'PRC_IUD_FUTURE_VACANCY',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": edit_admin_projected_vacancy_req_mapping,
        "response_mapping_function": edit_admin_projected_vacancy_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_admin_projected_vacancy_req_mapping(request):
    pvData = []
    for pv in request:
        pvData.append({
            'FV_SEQ_NUM': pv.get('future_vacancy_seq_num'),
            'FV_SEQ_NUM_REF': pv.get('future_vacancy_seq_num_ref'),
            'POS_SEQ_NUM': pv.get('positon_seq_num'),
            'BSN_ID': pv.get('bid_season_code'),
            'ASG_SEQ_NUM_EF': pv.get('assignment_seq_num_effective'),
            'ASG_SEQ_NUM': pv.get('assignment_seq_num'),
            'CDT_CD': pv.get('cycle_date_type_code'),
            'FVS_CODE': pv.get('future_vacancy_status_code'),
            'FVO_CODE': pv.get('future_vacancy_override_code'),
            'FV_OVERRIDE_TED_DATE': pv.get('future_vacancy_override_tour_end_date'),
            'FV_SYSTEM_IND': pv.get('future_vacancy_system_indicator'),
            'FV_COMMENT_TXT': pv.get('future_vacancy_comment'),
            'FV_CREATE_ID': pv.get('creator_id'),
            'FV_CREATE_DATE': pv.get('created_date'),
            'FV_UPDATE_ID': pv.get('updater_id'),
            'FV_UPDATE_DATE': pv.get('updated_date'),
            'FV_MC_IND': pv.get('future_vacancy_mc_indicator'),
            'FV_EXCL_IMPORT_IND': pv.get('future_vacancy_exclude_import_indicator'),
        })
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'pv_action_i': 'U',
        'pjson_fv_i': {
            'Data': pvData
        }
    }

def edit_admin_projected_vacancy_res_mapping(data):
    return service_response(data, 'Projected Vacancy Edit')

# ======================== Edit PV Language Offsets ========================

def edit_admin_projected_vacancy_lang_offsets(data, jwt_token):
    '''
    Edit Admin Projected Vacancy Language Offsets
    '''
    args = {
        "proc_name": 'PRC_IUD_POSITION_PLO',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": edit_admin_projected_vacancy_lang_offsets_req_mapping,
        "response_mapping_function": edit_admin_projected_vacancy_lang_offsets_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_admin_projected_vacancy_lang_offsets_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PX_LANGOS_I': f'''
            <ROWSET>
                <ROW>
                    <POS_SEQ_NUM>{request.get('positon_seq_num')}</POS_SEQ_NUM>
                    <LOT_SEQ_NUM>{request.get('language_offset_summer')}</LOT_SEQ_NUM>
                </ROW>
            </ROWSET>
        ''',
        'PX_LANGOW_I': f'''
            <ROWSET>
                <ROW>
                    <POS_SEQ_NUM>{request.get('positon_seq_num')}</POS_SEQ_NUM>
                    <LOT_SEQ_NUM>{request.get('language_offset_winter')}</LOT_SEQ_NUM>
                </ROW>
            </ROWSET>
        ''',
        'PV_RETURN_CODE_O': '',
        'PQRY_ERROR_DATA_O': ''
    }

def edit_admin_projected_vacancy_lang_offsets_res_mapping(data):
    return service_response(data, 'Projected Vacancy Edit Language Offsets')

# ======================== Edit PV Capsule Description ========================

def edit_admin_projected_vacancy_capsule_desc(data, jwt_token):
    '''
    Edit Admin Projected Vacancy Capsule Description
    '''
    args = {
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": edit_admin_projected_vacancy_capsule_desc_req_mapping,
        "response_mapping_function": edit_admin_projected_vacancy_capsule_desc_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_admin_projected_vacancy_capsule_desc_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'I_POS_SEQ_NUM': request.get('positon_seq_num'),
        'I_PPOS_CAPSULE_DESCR_TXT': request.get('capsule_description'),
        'I_PPOS_LAST_UPDT_USER_ID': request.get('updater_id'),
        'I_PPOS_LAST_UPDT_TMSMP_DT': request.get('updated_date'),
    }

def edit_admin_projected_vacancy_capsule_desc_res_mapping(data):
    return service_response(data, 'Projected Vacancy Edit Capsule Description')

# ======================== Get PV Metadata ========================

def get_admin_projected_vacancy_metadata(data, jwt_token):
    '''
    Get Admin Projected Vacancy Metadata
    '''
    args = {
        "proc_name": 'PRC_S_FUTURE_VACANCY',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": get_admin_projected_vacancy_metadata_req_mapping,
        "response_mapping_function": get_admin_projected_vacancy_metadata_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def get_admin_projected_vacancy_metadata_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PV_FV_SEQ_NUM_I': request.get('future_vacancy_seq_num'),
        'PQRY_CUST_FV_TAB_O': '',
        'PQRY_BSN_TAB_O': '',
        'PQRY_FVS_TAB_O': '',
        'PQRY_FVO_TAB_O': '',
        'PQRY_FV_ADMIN_O': '',
        'PV_RETURN_CODE_O': '',
        'PQRY_ERROR_DATA_O': '',
    }

def get_admin_projected_vacancy_metadata_res_mapping(response):
    def metadata_mapping(x):
        return {
            'creator_id': x.get('FV_CREATE_ID'),
            'created_date': x.get('FV_CREATE_DATE'),
            'updater_id': x.get('FV_UPDATE_ID'),
            'updated_date': x.get('FV_UPDATE_DATE'),
        }
    return service_response(response, 'Projected Vacancy Metadata', metadata_mapping)

# ======================== Get PV Language Offsets ========================

def get_admin_projected_vacancy_lang_offsets(data, jwt_token):
    '''
    Get Admin Projected Vacancy Language Offsets
    '''
    args = {
        "proc_name": 'prc_lst_pos_lang_results',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT98',
        "request_mapping_function": get_admin_projected_vacancy_lang_offsets_req_mapping,
        "response_mapping_function": get_admin_projected_vacancy_lang_offsets_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def get_admin_projected_vacancy_lang_offsets_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'PX_BUREAU_I': None,
        'PX_ORG_I': None,
        'PX_PAY_PLAN_I': None,
        'PX_GRADE_I': None,
        'PX_SKILL_I': None,
        'PX_LANGUAGE_I': None,
        'PX_CUST_TP_I': None,
        'PX_TOD_I': None,
        'PXML_POSITION_I': f'''
            <XMLSearchCriterias>
                <SearchList>
                    <Value>{request.get('position_seq_num')}</Value>
                </SearchList>
            </XMLSearchCriterias>
        ''',
        'PX_OVERSEAS_I': None,
        'PX_COUNTRY_I': None,
        'PQRY_FV_ADMIN_O': '',
        'PV_RETURN_CODE_O': '',
        'PQRY_ERROR_DATA_O': '',
    }

def get_admin_projected_vacancy_lang_offsets_res_mapping(response):
    def lang_offset_mapping(x):
        return {
            "language_offset_summer": x.get("LANG_OFFSET_SUMMER"),
            "language_offset_winter": x.get("LANG_OFFSET_WINTER"),
        }
    return service_response(response, 'Projected Vacancy Language Offsets', lang_offset_mapping)
