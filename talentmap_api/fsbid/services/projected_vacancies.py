import requests
import logging
import csv
from datetime import datetime
import maya

from functools import partial
from urllib.parse import urlencode, quote

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, QueryDict
from django.utils.encoding import smart_str

from talentmap_api.common.common_helpers import ensure_date, safe_navigation
import talentmap_api.fsbid.services.common as services
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

API_ROOT = settings.FSBID_API_URL
FAVORITES_LIMIT = settings.FAVORITES_LIMIT

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

def get_projected_vacancies_tandem(query, jwt_token, host=None):
    return services.send_get_request(
        "positions/futureVacancies/tandem",
        query,
        partial(convert_pv_query, isTandem=True),
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        get_projected_vacancies_tandem_count,
        "/api/v1/fsbid/projected_vacancies/tandem/",
        host
    )

def get_projected_vacancies_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    return services.send_count_request("futureVacanciesCount", query, convert_pv_query, jwt_token, host)

def get_projected_vacancies_tandem_count(query, jwt_token, host=None):
    '''
    Gets the total number of tandem PVs for a filterset
    '''
    return services.send_count_request("positions/futureVacancies/tandem", query, partial(convert_pv_query, isTandem=True), jwt_token, host)

def get_projected_vacancies_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "futureVacancies",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        "/api/v1/fsbid/projected_vacancies/",
        host,
        None,
        limit
    )

    count = get_projected_vacancies_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "projected_vacancies", False)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response

def get_projected_vacancies_tandem_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "positions/futureVacancies/tandem",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        "/api/v1/fsbid/projected_vacancies/tandem/",
        host,
        None,
        limit
    )

    count = get_projected_vacancies_tandem_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "projected_vacancies", False, True)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response


def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    return {
        "id": pv.get("fv_seq_num", None),
        "ted": ensure_date(pv.get("ted", None), utc_offset=-5),
        "bidcycle": {
            "id": pv.get("bsn_id", None),
            "name": pv.get("bsn_descr_text", None),
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": True
        },
        "tandem_nbr": pv.get("tandem_nbr", None), # Only appears in tandem searches
        "position": {
            "grade": pv.get("pos_grade_code", None),
            "skill": f"{pv.get('pos_skill_desc', None)} ({pv.get('pos_skill_code')})",
            "bureau": f"({pv.get('pos_bureau_short_desc', None)}) {pv.get('pos_bureau_long_desc', None)}",
            "skill": f"{pv.get('pos_skill_desc', None)} ({pv.get('pos_skill_code')})",
            "organization": f"({pv.get('org_short_desc', None)}) {pv.get('org_long_desc', None)}",
            "tour_of_duty": pv.get("tod", None),
            "languages": list(filter(None, [
                services.parseLanguage(pv.get("lang1", None)),
                services.parseLanguage(pv.get("lang2", None)),
            ])),
            "commuterPost": {
                "description": pv.get("cpn_desc", None),
                "frequency": pv.get("cpn_freq_desc", None),
            },
            "post": {
                "tour_of_duty": pv.get("tod", None),
                "post_overview_url": services.get_post_overview_url(pv.get("pos_location_code", None)),
                "post_bidding_considerations_url": services.get_post_bidding_considerations_url(pv.get("pos_location_code", None)),
                "obc_id": services.get_obc_id(pv.get("pos_location_code", None)),
                "differential_rate": pv.get("bt_differential_rate_num", None),
                "danger_pay": pv.get("bt_danger_pay_num", None),
                "location": {
                    "country": pv.get("location_country", None),
                    "code": pv.get("pos_location_code", None),
                    "city": pv.get("location_city", None),
                    "state": pv.get("location_state", None),
                },
            },
            "current_assignment": {
                "user": pv.get("incumbent", None),
                "estimated_end_date": ensure_date(pv.get("ted", None), utc_offset=-5)
            },
            "position_number": pv.get("position", None),
            "title": pv.get("pos_title_desc", None),
            "availability": {
                "availability": True,
                "reason": None
            },
            "bid_cycle_statuses": [
                {
                    "id": pv.get("fv_seq_num", None),
                    "bidcycle": pv.get("bsn_descr_text", None),
                    "position": pv.get("pos_title_desc", None),
                    "status_code": None,
                    "status": None
                }
            ],
            "latest_bidcycle": {
                "id": pv.get("bsn_id", None),
                "name": pv.get("bsn_descr_text", None),
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": True
            },
            "description": {
                "content": pv.get("ppos_capsule_descr_txt", None),
                "date_updated": ensure_date(pv.get("ppos_capsule_modify_dt", None), utc_offset=5),
            }
        },
        "unaccompaniedStatus": pv.get("us_desc_text", None),
        "isConsumable": pv.get("bt_consumable_allowance_flg", None) == "Y",
        "isServiceNeedDifferential": pv.get("bt_service_needs_diff_flg", None) == "Y",
        "isDifficultToStaff": pv.get("bt_most_difficult_to_staff_flg", None) == "Y",
        "isEFMInside": pv.get("bt_inside_efm_employment_flg", None) == "Y",
        "isEFMOutside": pv.get("bt_outside_efm_employment_flg", None) == "Y",
    }

def convert_pv_query(query, isTandem=False):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    prefix = "fv_request_params."

    if isTandem: prefix = "request_params."

    values = {
        # Pagination
        f"{prefix}order_by": services.sorting_values(query.get("ordering", None)),
        f"{prefix}page_index": int(query.get("page", 1)),
        f"{prefix}page_size": query.get("limit", 25),

        # Tandem 1 filters
        f"{prefix}seq_nums": services.convert_multi_value(query.get("id", None)),
        f"{prefix}bid_seasons": services.convert_multi_value(query.get("is_available_in_bidseason")),
        f"{prefix}overseas_ind": services.overseas_values(query),
        f"{prefix}languages": services.convert_multi_value(query.get("language_codes")),
        f"{prefix}bureaus": services.bureau_values(query),
        f"{prefix}grades": services.convert_multi_value(query.get("position__grade__code__in")),
        f"{prefix}location_codes": services.post_values(query),
        f"{prefix}danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        f"{prefix}differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        f"{prefix}pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        f"{prefix}post_ind": services.convert_multi_value(query.get("position__post_indicator__in")),
        f"{prefix}tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        f"{prefix}skills": services.convert_multi_value(query.get("position__skill__code__in")),
        f"{prefix}us_codes": services.convert_multi_value(query.get("position__us_codes__in")),
        f"{prefix}freeText": query.get("q", None),
    }

    if not isTandem:
        values[f"{prefix}get_count"]: query.get("getCount", 'false')

    if isTandem:
        ordering = query.get("ordering", None)
        values[f"{prefix}count"] = query.get("getCount", 'false')
        values[f"{prefix}order_by"] = services.sorting_values(f"commuterPost,location,tandem,{ordering}")
        # Common filters
        values[f"{prefix}overseas_ind2"] = services.overseas_values(query)
        values[f"{prefix}location_codes2"] = services.post_values(query)
        values[f"{prefix}danger_pays2"] = services.convert_multi_value(query.get("position__post__danger_pay__in"))
        values[f"{prefix}differential_pays2"] = services.convert_multi_value(query.get("position__post__differential_rate__in"))
        values[f"{prefix}post_ind2"] = services.convert_multi_value(query.get("position__post_indicator__in"))
        values[f"{prefix}us_codes2"] = services.convert_multi_value(query.get("position__us_codes__in"))
        values[f"{prefix}freeText2"] = query.get("q", None)

        # Tandem 2 filters
        values[f"{prefix}seq_nums2"] = services.convert_multi_value(query.get("id-tandem", None))
        values[f"{prefix}bid_seasons2"] = services.convert_multi_value(query.get("is_available_in_bidseason-tandem"))
        values[f"{prefix}languages2"] = services.convert_multi_value(query.get("language_codes-tandem"))
        values[f"{prefix}bureaus2"] = services.bureau_values(query, True)
        values[f"{prefix}grades2"] = services.convert_multi_value(query.get("position__grade__code__in-tandem"))
        values[f"{prefix}pos_numbers2"] = services.convert_multi_value(query.get("position__position_number__in-tandem", None))
        values[f"{prefix}tod_codes2"] = services.convert_multi_value(query.get("position__post__tour_of_duty__code__in-tandem"))
        values[f"{prefix}skills2"] = services.convert_multi_value(query.get("position__skill__code__in-tandem"))
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def archive_favorites(pvs, request, favoritesLimit=FAVORITES_LIMIT):
    favs_length = len(pvs)
    if favs_length >= favoritesLimit or favs_length == round(favoritesLimit/2):
        # Pos nums is string to pass correctly to services url
        pos_nums = ','.join(pvs)
        # List favs is list of integers instead of strings for comparison
        list_favs = list(map(lambda x: int(x), pvs))
        # Valid resulting ids from fsbid
        returned_ids = get_pv_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        # Need to determine which ids need to be archived using comparison of lists above
        outdated_ids = []
        if isinstance(returned_ids, list):
            for fav_id in list_favs:
                if fav_id not in returned_ids:
                    outdated_ids.append(fav_id)
            if len(outdated_ids) > 0:
                ProjectedVacancyFavorite.objects.filter(fv_seq_num__in=outdated_ids).update(archived=True)

def get_pv_favorite_ids(query, jwt_token, host=None):
    return services.send_get_request(
        "futureVacancies",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_favorites_to_talentmap_favorites_ids,
        get_projected_vacancies_count,
        "/api/v1/fsbid/projected_vacancies/",
        host
    ).get('results')

def fsbid_favorites_to_talentmap_favorites_ids(pv):
    return pv.get("fv_seq_num", None)
