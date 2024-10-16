import logging
import requests  # pylint: disable=unused-import
import pydash
import jwt
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import combine_pp_grade, service_response
from django.conf import settings

PV_API_V3_URL = settings.PV_API_V3_URL

logger = logging.getLogger(__name__)

# ======================== Get PV Filters ========================

def get_admin_projected_vacancy_filters(jwt_token):
    '''
    Gets Filters for Admin Projected Vacancies
    '''
    args = {
        "proc_name": "PRC_FV_ADMIN_SEARCH",
        "package_name": "PKG_WEBAPI_WRAP",
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

# ======================== Get PV Language Offset Options ========================

def get_admin_projected_vacancy_lang_offset_options(jwt_token):
    '''
    Gets Language Offset Options for Admin Projected Vacancies
    '''
    args = {
        "proc_name": "PRC_LST_POS_PLO_CRITERIA",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT98",
        "request_mapping_function": admin_projected_vacancy_filter_req_mapping,
        "response_mapping_function": admin_projected_vacancy_lang_offset_options_res_mapping,
        "jwt_token": jwt_token,
        "request_body": {},
    }
    return services.send_post_back_office(
        **args
    )

def admin_projected_vacancy_lang_offset_options_res_mapping(response):
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
        "uri": "",
        "query": query,
        "query_mapping_function": admin_projected_vacancy_req_mapping,
        "jwt_token": jwt_token,
        "mapping_function": admin_projected_vacancy_res_mapping,
        "count_function": get_projected_vacancy_count,
        "base_url": "/api/v3/futureVacancies/",
        "api_root": PV_API_V3_URL,
    }
    result = services.send_get_request(**args) 
    return result or None

def get_projected_vacancy_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": admin_projected_vacancy_req_mapping,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "is_template": True,
        "api_root": PV_API_V3_URL,
    }
    return services.send_count_request(**args)

def admin_projected_vacancy_req_mapping(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 10)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'posbureaucode', 'val': query.get("bureaus", None)},
            {'col': 'posorgshortdesc', 'val': query.get("organizations", None)},
            {'col': 'fvbsnid', 'val': query.get("bidSeasons", None)},
            {'col': 'posgradecode', 'val': query.get("grades", None)},
            {'col': 'posskillcode', 'val': query.get("skills", None)},
            {'col': 'poslanguage1code', 'val': query.get("languages", None)},
            {'col': 'poslanguage2code', 'val': query.get("languages", None)},
        ]),
    }
    if query.get("getCount") == 'true':
        values["rp.pageNum"] = 0
        values["rp.pageRows"] = 0
        values["rp.columns"] = "ROWCOUNT"

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def admin_projected_vacancy_res_mapping(response):
    # return service_response(response, 'Projected Vacancy List')
     return {
         **response,
         "combinedppgrade": combine_pp_grade(response.get("pospayplancode"), response.get("posgradecode")),
     }


# ======================== Edit PV ========================

def edit_admin_projected_vacancy(query, jwt_token):
    '''
    Edit Admin Projected Vacancy
    '''

    fvseqnum = query.get("data")

    # Inject decoded hru
    query['hru_id'] = jwt.decode(jwt_token, verify=False).get('sub')

    args = {
        "uri": f"v1/futureVacancies/{fvseqnum}",
        "query": query,
        "query_mapping_function": convert_admin_projected_vacancy_edit_query,
        "jwt_token": jwt_token,
        "mapping_function": None,
    }
    return services.send_put_request(**args)


def convert_admin_projected_vacancy_edit_query(query):
    values = {
        "fvfvscode": query.get("fvfvscode"),
        "fvoverrideteddate": query.get("fvoverrideteddate"),
        "fvbsnid": int(query.get("fvbsnid")),
        "fvcommenttxt": query.get("fvcommenttxt"),
        "fvexclimportind": query.get("fvexclimportind"),
        "fvseqnum": query.get("fvseqnum"),
        "fvseqnumref": query.get("fvfvseqnumref"),
        "fvposseqnum": query.get("fvposseqnum"),
        "fvasgseqnumef": query.get("fvasgseqnumef"),
        "fvasgseqnum": query.get("fvasgseqnum"),
        "fvcdtcd": query.get("fvcdtcd"),
        "fvfvocode": query.get("fvfvocode"),
        "fvsystemind": query.get("fvsystemind"),
        "fvcreateid": query.get("fvcreateid"),
        "fvcreatedate": query.get("fvcreatedate", "").replace("T", " "),
        "fvupdateid": query.get("hru_id"),
        "fvupdatedate": query.get("fvupdatedate", "").replace("T", " "),
        "fvmcind": query.get("fvmcind"),
    }
    return values

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
        'PX_LANGOS_I': f'<ROWSET><ROW><POS_SEQ_NUM>{request.get("position_seq_num")}</POS_SEQ_NUM><LOT_SEQ_NUM>{request.get("language_offset_summer") or ""}</LOT_SEQ_NUM></ROW></ROWSET>',
        'PX_LANGOW_I': f'<ROWSET><ROW><POS_SEQ_NUM>{request.get("position_seq_num")}</POS_SEQ_NUM><LOT_SEQ_NUM>{request.get("language_offset_winter") or ""}</LOT_SEQ_NUM></ROW></ROWSET>',
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
        'I_POS_SEQ_NUM': request.get('position_seq_num'),
        'I_PPOS_CAPSULE_DESCR_TXT': request.get('capsule_description'),
        'I_PPOS_LAST_UPDT_USER_ID': request.get('updater_id'),
        'I_PPOS_LAST_UPDT_TMSMP_DT': request.get('updated_date'),
    }

def edit_admin_projected_vacancy_capsule_desc_res_mapping(data):
    return service_response(data, 'Projected Vacancy Edit Capsule Description')

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
    search_list = ''
    position_numbers = request.get('position_numbers', '').split(',')
    for number in position_numbers:
        search_list += f'<Value>{number}</Value>'
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
        'PXML_POSITION_I': f'<XMLSearchCriterias><SearchList>{search_list}</SearchList></XMLSearchCriterias>',
        'PX_OVERSEAS_I': None,
        'PX_COUNTRY_I': None,
        'PQRY_FV_ADMIN_O': '',
        'PV_RETURN_CODE_O': '',
        'PQRY_ERROR_DATA_O': '',
    }

def get_admin_projected_vacancy_lang_offsets_res_mapping(response):
    def lang_offset_mapping(x):
        return {
            'position_seq_num': x.get('POS_SEQ_NUM'),
            'position_number': x.get('POS_NUM_TEXT'),
            'language_offset_summer': x.get('LANG_OFFSET_SUMMER'),
            'language_offset_winter': x.get('LANG_OFFSET_WINTER'),
        }
    def list_lang_offset_mapping(x):
        return list(map(lang_offset_mapping, x.get("PQRY_FVPL_ADMIN_O")))
    return service_response(response, 'Projected Vacancy Language Offsets List', list_lang_offset_mapping)
