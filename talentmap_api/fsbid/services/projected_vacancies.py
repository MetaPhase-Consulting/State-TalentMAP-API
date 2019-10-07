import requests
import logging

from urllib.parse import urlencode, quote

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from talentmap_api.common.common_helpers import ensure_date, safe_navigation
from talentmap_api.organization.models import Location
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_projected_vacancy(id, jwt_token):
    '''
    Gets an indivdual projected vacancy by id
    '''
    return services.get_individual(
        "futureVacancies",
        id,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv
    )
def get_projected_vacancies(query, jwt_token, host=None):
    return services.send_get_request(
        "futureVacancies",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        get_projected_vacancies_count,
        "/api/v1/fsbid/projected_vacancies/",
        host
    )


def get_projected_vacancies_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    return services.send_count_request("futureVacanciesCount", query, convert_pv_query, jwt_token, host)



def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    location = {}
    try:
        location = Location.objects.get(code=pv.get("pos_location_code", ""))
    except ObjectDoesNotExist:
        logger.warning(f"No location with code {pv.get("pos_location_code", "")} was found.")
    return {
        "id": pv.get("fv_seq_num", ""),
        "ted": ensure_date(pv.get("ted", ""), utc_offset=-5),
        "bidcycle": {
            "id": pv.get("bsn_id", ""),
            "name": pv.get("bsn_descr_text", ""),
            "cycle_start_date": "",
            "cycle_deadline_date": "",
            "cycle_end_date": "",
            "active": True
        },
        "position": {
            "grade": pv.get("pos_grade_code", ""),
            "skill": pv.get("pos_skill_desc", ""),
            "bureau": pv.get("bureau_desc", ""),
            "organization": pv.get("post_org_country_state", ""),
            "tour_of_duty": pv.get("tod", ""),
            "languages": list(filter(None, [
                services.parseLanguage(pv.get("lang1", "")),
                services.parseLanguage(pv.get("lang2", "")),
            ])),
            "post": {
                "tour_of_duty": pv.get("tod", ""),
                "differential_rate": pv.get("bt_differential_rate_num", ""),
                "danger_pay": pv.get("bt_danger_pay_num", ""),
                "location": {
                    "id": safe_navigation(location, 'id'),
                    "country": f"{safe_navigation(location, 'country')}",
                    "code": safe_navigation(location, 'code'),
                    "city": safe_navigation(location, 'city'),
                    "state": safe_navigation(location, 'state')
                }
            },
            "current_assignment": {
                "user": pv.get("incumbent", ""),
                "estimated_end_date": ensure_date(pv.get("ted", ""), utc_offset=-5)
            },
            "position_number": pv.get("position", ""),
            "title": pv.get("pos_title_desc", ""),
            "availability": {
                "availability": True,
                "reason": ""
            },
            "bid_cycle_statuses": [
                {
                    "id": pv.get("fv_seq_num", ""),
                    "bidcycle": pv.get("bsn_descr_text", ""),
                    "position": pv.get("pos_title_desc", ""),
                    "status_code": "",
                    "status": ""
                }
            ],
            "latest_bidcycle": {
                "id": pv.get("bsn_id", ""),
                "name": pv.get("bsn_descr_text", ""),
                "cycle_start_date": "",
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "active": True
            },
            "description": {
                "content": pv.get("ppos_capsule_descr_txt", "")
            }
        }
    }

def convert_pv_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "fv_request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "fv_request_params.page_index": int(query.get("page", 1)),
        "fv_request_params.page_size": query.get("limit", 25),
        "fv_request_params.freeText": query.get("q", None),
        "fv_request_params.bid_seasons": services.convert_multi_value(query.get("is_available_in_bidseason")),
        "fv_request_params.bureaus": services.bureau_values(query),
        "fv_request_params.overseas_ind": services.overseas_values(query),
        "fv_request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "fv_request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "fv_request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "fv_request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "fv_request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "fv_request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "fv_request_params.location_codes": services.post_values(query),
        "fv_request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "fv_request_params.seq_nums": services.convert_multi_value(query.get("id", None)),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
