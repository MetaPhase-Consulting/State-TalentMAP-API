import requests
import logging

from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.organization.models import Post, Organization, OrganizationGroup
from talentmap_api.available_positions.models import AvailablePositionDesignation
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def get_available_positions(query, jwt_token, host=None):
    return services.send_get_request(
        "availablePositions",
        query,
        convert_ap_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        get_available_positions_count,
        "/api/v1/fsbid/available_positions/",
        host
    )


def get_available_positions_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    return services.send_count_request("availablePositionsCount", query, convert_ap_query, jwt_token, host)


def fsbid_ap_to_talentmap_ap(ap):
    '''
    Converts the response available position from FSBid to a format more in line with the Talentmap position
    '''
    designations = AvailablePositionDesignation.objects.filter(cp_id=ap["cp_id"]).first()
    return {
        "id": ap["cp_id"],
        "status": "",
        "status_code": ap["cp_status"],
        "ted": ensure_date(ap["ted"], utc_offset=-5),
        "posted_date": ensure_date(ap["cp_post_dt"], utc_offset=-5),
        "availability": {
            "availability": "",
            "reason": ""
        },
        "is_urgent_vacancy": getattr(designations, 'is_urgent_vacancy', False),
        "is_volunteer": getattr(designations, 'is_volunteer', False),
        "is_hard_to_fill": getattr(designations, 'is_hard_to_fill', False),
        "position": {
            "id": "",
            "grade": ap["pos_grade_code"],
            "skill": ap["pos_skill_desc"],
            "bureau": ap["pos_bureau_short_desc"],
            "organization": ap["post_org_country_state"],
            "tour_of_duty": ap["tod"],
            "classifications": "",
            "representation": "",
            "availability": {
                "availability": "",
                "reason": ""
            },
            "position_number": ap["position"],
            "title": ap["pos_title_desc"],
            "is_overseas": "",
            "is_highlighted": getattr(designations, 'is_highlighted', False),
            "create_date": "",
            "update_date": "",
            "effective_date": "",
            "posted_date": ensure_date(ap["cp_post_dt"], utc_offset=-5),
            "description": {
                "id": "",
                "last_editing_user": "",
                "is_editable_by_user": "",
                "date_created": "",
                "date_updated": "",
                "content": ap["ppos_capsule_descr_txt"],
                "point_of_contact": "",
                "website": ""
            },
            "current_assignment": {
                "user": ap["incumbent"],
                "tour_of_duty": ap["tod"],
                "status": "",
                "start_date": "",
                "estimated_end_date": ensure_date(ap["ted"], utc_offset=-5)
            },
            "post": {
                "id": "",
                "code": ap["pos_location_code"],
                "tour_of_duty": ap["tod"],
                "post_overview_url": "",
                "post_bidding_considerations_url": "",
                "cost_of_living_adjustment": "",
                "differential_rate": ap["bt_differential_rate_num"],
                "danger_pay": ap["bt_danger_pay_num"],
                "rest_relaxation_point": "",
                "has_consumable_allowance": "",
                "has_service_needs_differential": "",
                "obc_id": "",
                "location": {
                    "id": "",
                    "country": "",
                    "code": "",
                    "city": "",
                    "state": ""
                }
            },
            "latest_bidcycle": {
                "id": ap["cycle_id"],
                "name": ap["cycle_nm_txt"],
                "cycle_start_date": "",
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "active": ""
            },
            "languages": list(filter(None, [
                services.parseLanguage(ap["lang1"]),
                services.parseLanguage(ap["lang2"]),
            ])),
        },
        "bidcycle": {
            "id": ap["cycle_id"],
            "name": ap["cycle_nm_txt"],
            "cycle_start_date": "",
            "cycle_deadline_date": "",
            "cycle_end_date": "",
            "active": ""
        },
        "bid_statistics": {
            "id": "",
            "total_bids": ap["cp_ttl_bidder_qty"],
            "in_grade": ap["cp_at_grd_qty"],
            "at_skill": ap["cp_in_cone_qty"],
            "in_grade_at_skill": ap["cp_at_grd_in_cone_qty"],
            "has_handshake_offered": "",
            "has_handshake_accepted": ""
        }
    }

def convert_ap_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.page_index": int(query.get("page", 1)),
        "request_params.page_size": query.get("limit", 25),
        "request_params.freeText": query.get("q", None),
        "request_params.cps_codes": services.convert_multi_value("OP,HS"),
        "request_params.assign_cycles": services.convert_multi_value(query.get("is_available_in_bidseason")),
        "request_params.bureaus": services.bureau_values(query),
        "request_params.overseas_ind": services.overseas_values(query),
        "request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "request_params.location_codes": services.post_values(query),
        "request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "request_params.cp_ids": services.convert_multi_value(query.get("id", None)),
    }
    return urlencode({i: j for i, j in values.items() if j is not None})
