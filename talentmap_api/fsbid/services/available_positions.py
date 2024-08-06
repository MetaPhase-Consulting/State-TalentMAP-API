import logging
from functools import partial

import pydash
from django.conf import settings
import requests  # pylint: disable=unused-import

from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import ensure_date, validate_values
from talentmap_api.available_positions.models import AvailablePositionDesignation


logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT
CP_API_V2_URL = settings.CP_API_V2_URL


def get_available_position(id, jwt_token):
    '''
    Gets an individual available position by id
    '''

    args = {
        "uri": "available",
        "query": {"id": id},
        "query_mapping_function": convert_all_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_ap_to_talentmap_ap,
        "use_post": True,
        "api_root": CP_API_V2_URL,
        "count_function": None,
        "base_url": "/api/v1/fsbid/available_positions/",
    }

    ap_position = services.send_get_request(
        **args
    )

    return pydash.get(ap_position, 'results[0]') or None


def get_unavailable_position(id, jwt_token):
    '''
    Gets an individual unavailable position by id
    '''
    ua_pos = services.send_get_request(
        "availablePositions",
        {"id": id},
        convert_up_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        None,
        "/api/v1/fsbid/available_positions/"
    )

    return pydash.get(ua_pos, 'results[0]') or None


def get_all_position(id, jwt_token):
    '''
    Gets an individual cycle position by id
    '''

    args = {
        "uri": "",
        "query": {"id": id},
        "query_mapping_function": convert_all_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_ap_to_talentmap_ap,
        "use_post": True,
        "api_root": CP_API_V2_URL,
        "count_function": None,
        "base_url": "/api/v1/fsbid/cdo/",
    }

    position = services.send_get_request(
        **args
    )

    return pydash.get(position, 'results[0]') or None


def get_available_positions(query, jwt_token, host=None):
    '''
    Gets available positions
    '''

    args = {
        "uri": "available",
        "query": query,
        "query_mapping_function": convert_ap_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_ap_to_talentmap_ap,
        "count_function": get_available_positions_count,
        "base_url": "/api/v1/fsbid/available_positions/",
        "host": host,
        "use_post": True,
        "api_root": CP_API_V2_URL,
    }

    return services.send_get_request(
        **args
    )


def get_available_positions_tandem(query, jwt_token, host=None):
    '''
    Gets available positions
    '''
    args = {
        "uri": "availableTandem",
        "query": query,
        "query_mapping_function": partial(convert_ap_query, isTandem=True),
        "jwt_token": jwt_token,
        "mapping_function": fsbid_ap_to_talentmap_ap,
        "count_function": partial(get_available_positions_tandem_count),
        "base_url": "/api/v1/fsbid/available_positions/tandem/",
        "host": host,
        "use_post": True,
        "api_root": CP_API_V2_URL,
    }

    return services.send_get_request(
        **args
    )


def get_available_positions_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    args = {
        "uri": "availableCount",
        "query": query,
        "query_mapping_function": convert_ap_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": True,
        "api_root": CP_API_V2_URL,
    }
    return services.send_count_request(**args)


def get_available_positions_tandem_count(query, jwt_token, host=None):
    '''
    Gets the total number of available tandem positions for a filterset
    '''
    args = {
        "uri": "availableTandem",
        "query": query,
        "query_mapping_function": partial(convert_ap_query, isTandem=True),
        "jwt_token": jwt_token,
        "host": host,
        "use_post": True,
        "api_root": CP_API_V2_URL,
    }
    return services.send_count_request(**args)


def get_available_positions_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "available",
        query,
        convert_ap_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        CP_API_V2_URL,
        host,
        None,
        limit,
        True,
    )

    count = get_available_positions_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "available_positions", True)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response


def get_available_positions_tandem_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "availableTandem",
        query,
        partial(convert_ap_query, isTandem=True),
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        CP_API_V2_URL,
        host,
        None,
        limit,
        True,
    )

    count = get_available_positions_tandem_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "available_positions_tandem", True, True)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response


# Max number of similar positions to return.
SIMILAR_LIMIT = 50

# Filters available positions by the criteria provides and by the position with the provided id


def filter_available_positions_exclude_self(id, criteria, jwt_token, host):
    # Add 1 to the limit, since we'll be filtering out positions that match id
    a = list(filter(lambda i: float(id) != i["id"], get_available_positions({**criteria, **{"limit": SIMILAR_LIMIT + 1}}, jwt_token, host)["results"]))
    # Ensure we only return the limit, at most
    return a[:SIMILAR_LIMIT]


def get_similar_available_positions(id, jwt_token, host=None):
    '''
    Returns a query set of similar positions, using the base criteria.
    If there are not at least 3 results, the criteria is loosened.
    '''
    ap = get_available_position(id, jwt_token)
    base_criteria = {
        "position__post__code__in": ap["position"]["post"]["code"],
        "position__skill__code__in": ap["position"]['skill_code'],
        "position__grade__code__in": ap["position"]["grade"],
    }

    results = filter_available_positions_exclude_self(id, base_criteria, jwt_token, host)
    while len(results) < SIMILAR_LIMIT and len(base_criteria.keys()) > 0:
        del base_criteria[list(base_criteria.keys())[0]]
        results = filter_available_positions_exclude_self(id, base_criteria, jwt_token, host)

    return {"results": results}


def fsbid_ap_to_talentmap_ap(ap):
    '''
    Converts the response available position from FSBid to a format more in line with the Talentmap position
    '''
    designations = AvailablePositionDesignation.objects.filter(cp_id=ap.get("cp_id", None)).first()

    hasHandShakeOffered = False
    if ap.get("cp_status", None) == "HS":
        hasHandShakeOffered = True
    ted = ensure_date(ap.get("cp_ted_ovrrd_dt", None), utc_offset=-5)
    if ted is None:
        ted = ensure_date(ap.get("ted", None), utc_offset=-5)

    skill2 = services.get_secondary_skill(ap)
    return {
        "id": ap.get("cp_id", None),
        "status": None,
        "status_code": ap.get("cp_status", None),
        "ted": ted,
        "posted_date": ensure_date(ap.get("cp_post_dt", None), utc_offset=-5),
        "availability": {
            "availability": None,
            "reason": None
        },
        "tandem_nbr": ap.get("tandem_nbr", None),  # Only appears in tandem searches
        "position": {
            "id": None,
            "grade": ap.get("pos_grade_code", None),
            "skill": f"{ap.get('pos_skill_desc', None)} ({ap.get('pos_skill_code')})",
            "skill_code": ap.get("pos_skill_code", None),
            "skill_secondary": skill2.get("skill_secondary"),
            "skill_secondary_code": skill2.get("skill_secondary_code"),
            "bureau": f"({ap.get('pos_bureau_short_desc', None)}) {ap.get('pos_bureau_long_desc', None)}",
            "bureau_code": ap.get('bureau_code', None),
            "organization": f"({ap.get('org_short_desc', None)}) {ap.get('org_long_desc', None)}",
            "organization_code": ap.get('org_code', None),
            "tour_of_duty": ap.get("tod", None),
            "classifications": None,
            "representation": None,
            "availability": {
                "availability": None,
                "reason": None
            },
            "position_number": ap.get("position", None),
            "title": ap.get("pos_title_desc", None),
            "is_overseas": None,
            "is_highlighted": getattr(designations, 'is_highlighted', False),
            "create_date": None,
            "update_date": None,
            "effective_date": None,
            "posted_date": ensure_date(ap.get("cp_post_dt", None), utc_offset=-5),
            "description": {
                "id": None,
                "last_editing_user": None,
                "is_editable_by_user": None,
                "date_created": None,
                "date_updated": ensure_date(ap.get("ppos_capsule_modify_dt", None), utc_offset=5),
                "content": ap.get("ppos_capsule_descr_txt", None),
                "point_of_contact": None,
                "website": None
            },
            "current_assignment": {
                "user": ap.get("incumbent", None),
                "tour_of_duty": ap.get("tod", None),
                "status": None,
                "start_date": None,
                "estimated_end_date": ensure_date(ap.get("ted", None), utc_offset=-5)
            },
            "commuterPost": {
                "description": ap.get("cpn_desc", None),
                "frequency": ap.get("cpn_freq_desc", None),
            },
            "post": {
                "id": None,
                "code": ap.get("pos_location_code", None),
                "tour_of_duty": ap.get("tod", None),
                "post_overview_url": services.get_post_overview_url(ap.get("pos_location_code", None)),
                "post_bidding_considerations_url": services.get_post_bidding_considerations_url(ap.get("pos_location_code", None)),
                "cost_of_living_adjustment": None,
                "differential_rate": ap.get("bt_differential_rate_num", None),
                "danger_pay": ap.get("bt_danger_pay_num", None),
                "rest_relaxation_point": None,
                "has_consumable_allowance": None,
                "has_service_needs_differential": None,
                "obc_id": services.get_obc_id(ap.get("pos_location_code", None)),
                "location": {
                    "country": ap.get("location_country", None),
                    "code": ap.get("pos_location_code", None),
                    "city": ap.get("location_city", None),
                    "state": ap.get("location_state", None),
                },
            },
            "latest_bidcycle": {
                "id": ap.get("cycle_id", None),
                "name": ap.get("cycle_nm_txt", None),
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": None
            },
            "languages": list(filter(None, [
                services.parseLanguage(ap.get("lang1", None)),
                services.parseLanguage(ap.get("lang2", None)),
            ])),
        },
        "bidcycle": {
            "id": ap.get("cycle_id", None),
            "name": ap.get("cycle_nm_txt", None),
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": None
        },
        "bid_statistics": [{
            "id": None,
            "total_bids": ap.get("cp_ttl_bidder_qty", None),
            "in_grade": ap.get("cp_at_grd_qty", None),
            "at_skill": ap.get("cp_in_cone_qty", None),
            "in_grade_at_skill": ap.get("cp_at_grd_in_cone_qty", None),
            "has_handshake_offered": hasHandShakeOffered,
            "has_handshake_accepted": None
        }],
        "unaccompaniedStatus": ap.get("us_desc_text", None),
        "isConsumable": ap.get("bt_consumable_allowance_flg", None) == "Y",
        "isServiceNeedDifferential": ap.get("bt_service_needs_diff_flg", None) == "Y",
        "isDifficultToStaff": ap.get("bt_most_difficult_to_staff_flg", None) == "Y",
        "isEFMInside": ap.get("bt_inside_efm_employment_flg", None) == "Y",
        "isEFMOutside": ap.get("bt_outside_efm_employment_flg", None) == "Y",
        "isHardToFill": ap.get("acp_hard_to_fill_ind", None) == "Y",
        "isCritNeed": ap.get("cp_critical_need_ind", None) == "Y",
    }


def convert_ap_query(query, allowed_status_codes=["HS", "OP"], isTandem=False):
    '''
    Converts TalentMap filters into FSBid filters
    '''

    prefix = ""

    values = {
        # Pagination
        f"{prefix}order_by": services.sorting_values(query.get("ordering", None), True),
        f"{prefix}page_index": int(query.get("page", 1)),
        f"{prefix}page_size": query.get("limit", 25),

        # Tandem 1 filters
        f"{prefix}cps_codes": services.convert_multi_value(
            validate_values(query.get("cps_codes", "HS,OP,FP"), allowed_status_codes)),
        f"{prefix}cp_ids": services.convert_multi_value(query.get("id", None)),
        f"{prefix}assign_cycles": services.convert_multi_value(query.get("is_available_in_bidcycle")),
        f"{prefix}overseas_ind": services.convert_multi_value(services.overseas_values(query)),
        f"{prefix}languages": services.convert_multi_value(query.get("language_codes")),
        f"{prefix}bureaus": services.convert_multi_value(query.get("position__bureau__code__in")),
        f"{prefix}grades": services.convert_multi_value(query.get("position__grade__code__in")),
        f"{prefix}location_codes": services.post_values(query),
        f"{prefix}danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        f"{prefix}differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        f"{prefix}pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        f"{prefix}post_ind": services.convert_multi_value(query.get("position__post_indicator__in")),
        f"{prefix}tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        f"{prefix}skills": services.convert_multi_value(query.get("position__skill__code__in")),
        f"{prefix}us_codes": services.convert_multi_value(query.get("position__us_codes__in")),
        f"{prefix}cpn_codes": services.convert_multi_value(query.get("position__cpn_codes__in")),
        f"{prefix}htf_ind": services.convert_multi_value(query.get("htf_indicator")),
        f"{prefix}cp_critical_need_ind": services.convert_multi_value(query.get("cn_indicator")),
        f"{prefix}freeText": query.get("q", None),

    }

    if not isTandem:
        values[f"{prefix}get_count"] = query.get("getCount", 'false')

    if isTandem:
        ordering = query.get("ordering", None)
        values[f"{prefix}count"] = query.get("getCount", 'false')
        values[f"{prefix}order_by"] = services.sorting_values(f"commuterPost,location,location_code,tandem,{ordering}", True)
        # Common filters
        values[f"{prefix}overseas_ind2"] = services.convert_multi_value(services.overseas_values(query))
        values[f"{prefix}location_codes2"] = services.post_values(query)
        values[f"{prefix}danger_pays2"] = services.convert_multi_value(query.get("position__post__danger_pay__in"))
        values[f"{prefix}differential_pays2"] = services.convert_multi_value(query.get("position__post__differential_rate__in"))
        values[f"{prefix}post_ind2"] = services.convert_multi_value(query.get("position__post_indicator__in"))
        values[f"{prefix}us_codes2"] = services.convert_multi_value(query.get("position__us_codes__in"))
        values[f"{prefix}cpn_codes2"] = services.convert_multi_value(query.get("position__cpn_codes__in"))
        values[f"{prefix}freeText2"] = query.get("q", None)

        # Tandem 2 filters
        values[f"{prefix}cps_codes2"] = services.convert_multi_value(
            validate_values(query.get("cps_codes-tandem", "HS,OP,FP"), allowed_status_codes))
        values[f"{prefix}cp_ids2"] = services.convert_multi_value(query.get("id-tandem", None))
        values[f"{prefix}assign_cycles2"] = services.convert_multi_value(query.get("is_available_in_bidcycle-tandem"))
        values[f"{prefix}languages2"] = services.convert_multi_value(query.get("language_codes-tandem"))
        values[f"{prefix}bureaus2"] = services.convert_multi_value(query.get("position__bureau__code__in-tandem"))
        values[f"{prefix}grades2"] = services.convert_multi_value(query.get("position__grade__code__in-tandem"))
        values[f"{prefix}pos_numbers2"] = services.convert_multi_value(query.get("position__position_number__in-tandem", None))
        values[f"{prefix}tod_codes2"] = services.convert_multi_value(query.get("position__post__tour_of_duty__code__in-tandem"))
        values[f"{prefix}skills2"] = services.convert_multi_value(query.get("position__skill__code__in-tandem"))
        values[f"{prefix}htf_ind2"] = services.convert_multi_value(query.get("htf_indicator-tandem"))
        values[f"{prefix}cp_critical_need_ind2"] = services.convert_multi_value(query.get("cn_indicator-tandem"))

    if isinstance(values[f"{prefix}order_by"], list):
        values[f"{prefix}order_by"] = pydash.compact(values[f"{prefix}order_by"])

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return valuesToReturn


def convert_up_query(query):
    '''
    sends FP (Filled Position) status code to convert_ap_query
    request_params.cps_codes of anything but FP will get removed from query
    '''
    return convert_ap_query(query, ["FP"])


def convert_all_query(query):
    '''
    sends FP(Filled Position), OP(Open Position), and HS(HandShake) status codes
    to convert_ap_query request_params.cps_codes of anything
    but FP, OP, or HS will get removed from query
    '''
    return convert_ap_query(query, ["FP", "OP", "HS"], False)


def get_ap_favorite_ids(query, jwt_token, host=None):
    return services.send_get_request(
        "available",
        query,
        convert_ap_query,
        jwt_token,
        fsbid_favorites_to_talentmap_favorites_ids,
        get_available_positions_count,
        "/api/v1/fsbid/available_positions/",
        host,
        CP_API_V2_URL,
        True,
    ).get('results')


def fsbid_favorites_to_talentmap_favorites_ids(ap):
    return ap.get("cp_id", None)
