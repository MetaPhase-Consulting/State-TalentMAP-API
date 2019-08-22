import requests
import re
import logging

from urllib.parse import urlencode

from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.organization.models import Post, Organization, OrganizationGroup
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_projected_vacancies(query, jwt_token, host=None):
    '''
    Gets projected vacancies from FSBid
    '''
    url = f"{API_ROOT}/futureVacancies?{convert_pv_query(query)}&fv_request_params.ad_id={services.get_adid_from_jwt(jwt_token)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    projected_vacancies = map(fsbid_pv_to_talentmap_pv, response["Data"])
    return {
        **services.get_pagination(query, get_projected_vacancies_count(query, jwt_token)['count'], "/api/v1/fsbid/projected_vacancies/", host),
        "results": projected_vacancies
    }


def get_projected_vacancies_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    url = f"{API_ROOT}/futureVacanciesCount?{convert_pv_query(query)}&fv_request_params.ad_id={services.get_adid_from_jwt(jwt_token)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return {"count": response["Data"][0]["count(1)"]}

# Pattern for extracting language parts from a string. Ex. "Spanish (3/3)"
LANG_PATTERN = re.compile("(.*?)\(.*\)\s(\d)/(\d)")

def parseLanguage(lang):
    '''
    Parses a language string from FSBid and turns it into what we want
    The lang param comes in as something like "Spanish (3/3)"
    '''
    if lang:
        match = LANG_PATTERN.search(lang)
        if match:
            language = {}
            language["language"] = match.group(1)
            language["reading_proficiency"] = match.group(2)
            language["spoken_proficiency"] = match.group(3)
            language["representation"] = match.group(0).rstrip()
            return language

def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    return {
        "id": pv["fv_seq_number"],
        "ted": ensure_date(pv["ted"], utc_offset=-5),
        "bidcycle": {
            "id": pv["bsn_id"],
            "name": pv["bsn_descr_text"],
            "cycle_start_date": "",
            "cycle_deadline_date": "",
            "cycle_end_date": "",
            "active": True
        },
        "position": {

            "grade": pv["pos_grade_code"],
            "skill": pv["pos_skill_desc"],
            "bureau": pv["bureau_desc"],
            "organization": pv["post_org_country_state"],
            "tour_of_duty": pv["tod"],
            "languages": list(filter(None, [
                parseLanguage(pv["lang1"]),
                parseLanguage(pv["lang2"]),
            ])),
            "post": {
                "tour_of_duty": pv["tod"],
                "differential_rate": pv["bt_differential_rate_num"],
                "danger_pay": pv["bt_danger_pay_num"],
                "location": {
                    "id": 7,
                    "country": "",
                    "code": "",
                    "city": "",
                    "state": ""
                }
            },
            "current_assignment": {
                "user": pv["incumbent"],
                "estimated_end_date": ensure_date(pv["ted"], utc_offset=-5)
            },
            "position_number": pv["position"],
            "title": pv["post_title_desc"],
            "availability": {
                "availability": True,
                "reason": ""
            },
            "bid_cycle_statuses": [
                {
                    "id": pv["fv_seq_number"],
                    "bidcycle": pv["bsn_descr_text"],
                    "position": pv["post_title_desc"],
                    "status_code": "",
                    "status": ""
                }
            ],
            "latest_bidcycle": {
                "id": pv["bsn_id"],
                "name": pv["bsn_descr_text"],
                "cycle_start_date": "",
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "active": True
            }
        }
    }

def post_values(query):
    '''
    Handles mapping locations and groups of locations to FSBid expected params
    '''
    results = []
    if query.get("is_domestic") == "true":
        domestic_codes = Post.objects.filter(location__country__code="USA").values_list("_location_code", flat=True)
        results = results + list(domestic_codes)
    if query.get("is_domestic") == "false":
        overseas_codes = Post.objects.exclude(location__country__code="USA").values_list("_location_code", flat=True)
        results = results + list(overseas_codes)
    if query.get("position__post__in"):
        post_ids = query.get("position__post__in").split(",")
        location_codes = Post.objects.filter(id__in=post_ids).values_list("_location_code", flat=True)
        results = results + list(location_codes)
    if len(results) > 0:
        return ",".join(results)

def bureau_values(query):
    '''
    Gets the ids for the functional/regional bureaus and maps to codes and their children
    '''
    results = []
    # functional bureau filter
    if query.get("org_has_groups"):
        func_bureaus = query.get("org_has_groups").split(",")
        func_org_codes = OrganizationGroup.objects.filter(id__in=func_bureaus).values_list("_org_codes", flat=True)
        # Flatten _org_codes
        func_bureau_codes = [item for sublist in func_org_codes for item in sublist]
        results = results + list(func_bureau_codes)
    # Regional bureau filter
    if query.get("position__bureau__code__in"):
        regional_bureaus = query.get("position__bureau__code__in").split(",")
        reg_org_codes = Organization.objects.filter(Q(code__in=regional_bureaus) | Q(_parent_organization_code__in=regional_bureaus)).values_list("code", flat=True)
        results = results + list(reg_org_codes)
    if len(results) > 0:
        return ",".join(results)

def convert_pv_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "fv_request_params.page_index": int(query.get("page", 1)),
        "fv_request_params.page_size": query.get("limit", 25),
        "fv_request_params.freeText": query.get("q", None),
        "fv_request_params.bid_seasons": query.get("is_available_in_bidseason"),
        "fv_request_params.bureaus": bureau_values(query),
        "fv_request_params.danger_pays": query.get("position__post__danger_pay__in"),
        "fv_request_params.grades": query.get("position__grade__code__in"),
        "fv_request_params.languages": query.get("language_codes"),
        "fv_request_params.differential_pays": query.get("position__post__differential_rate__in"),
        "fv_request_params.skills": query.get("position__skill__code__in"),
        "fv_request_params.tod_codes": query.get("position__post__tour_of_duty__code__in"),
        "fv_request_params.location_codes": post_values(query),
        "fv_request_params.pos_numbers": query.get("position__position_number__in", None),
        "fv_request_params.fv_seq_number": query.get("id", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None})
