import logging
import requests  # pylint: disable=unused-import
from talentmap_api.fsbid.services import common as services


logger = logging.getLogger(__name__)

def get_admin_projected_vacancy_filters(jwt_token):
    '''
    Gets Filters for admin projected_vacancies 
    '''
    args = {
        "proc_name": "PRC_FV_ADMIN_SEARCH",
        "package_name": "PKG_WEBAPI_WRAP",
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


