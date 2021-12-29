import logging
import jwt
import pydash
from functools import partial
from urllib.parse import urlencode, quote

from django.conf import settings

from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import ensure_date

AGENDA_ITEM_API_ROOT = settings.AGENDA_ITEM_API_URL

logger = logging.getLogger(__name__)


def get_single_agenda_item(jwt_token=None, ai_id = None):
    '''
    Get single agenda item
    '''
    args = {
        "uri": "",
        "id": ai_id,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
        "use_id": False,
    }

    agenda_item = services.get_individual(
        **args
    )

    return agenda_item


def get_agenda_items(jwt_token=None, query = {}, host=None):
    '''
    Get agenda items
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_agenda_items_to_talentmap_agenda_items, jwt_token=jwt_token),
        "count_function": None,
        "base_url": "/api/v1/agenda_items/",
        "host": host,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
    }

    agenda_items = services.send_get_request(
        **args
    )

    return agenda_items

# Placeholder. Isn't used and doesn't work.
def get_agenda_items_count(query, jwt_token, host=None, use_post=False):
    '''
    Gets the total number of agenda items for a filterset
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
    }
    return services.send_count_request(**args)


def convert_agenda_item_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": query.get("limit", 1000),
        "rp.columns": None,
        "rp.order_by": services.sorting_values(query.get("ordering", "agenda_id")),
        "rp.filter": services.convert_to_fsbid_ql('aiperdetseqnum', query.get("perdet", None)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_single_agenda_item_to_talentmap_single_agenda_item(data):

    legsToReturn = []
    assignment = fsbid_aia_to_talentmap_aia(
                pydash.get(data, "agendaAssignment[0]", {})
            )
    legs = (list(map(
                fsbid_legs_to_talentmap_legs, pydash.get(data, "agendaLegs", [])
            )))
    legsToReturn.extend([assignment])
    legsToReturn.extend(legs)

    return {
        "id": data.get("aiseqnum", None),
        "remarks": services.parse_agenda_remarks(data.get("aicombinedremarktext", '')),
        "panel_date": ensure_date(pydash.get(data, "Panel.pmddttm", None), utc_offset=-5),
        "status": data.get("aisdesctext", None),
        "perdet": data.get("aiperdetseqnum", None),

        "assignment": fsbid_aia_to_talentmap_aia(
            pydash.get(data, "agendaAssignment[0]", {})
        ),

        "legs": legsToReturn,

        "update_date": ensure_date(data.get("update_date", None), utc_offset=-5), # TODO - find this date
        "modifier_name": data.get("aiupdateid", None), # TODO - this is only the id
        "creator_name": data.get("aiitemcreatorid", None), # TODO - this is only the id
    }


def fsbid_agenda_items_to_talentmap_agenda_items(data, jwt_token = None):
    ai_id = data.get("aiseqnum", None)

    agenda_item = get_single_agenda_item(jwt_token, ai_id)

    return {
        "id": data.get("aiseqnum", None),
        **agenda_item,
    }


def fsbid_legs_to_talentmap_legs(data):

    return {
        "id": pydash.get(data, "ailaiseqnum", None),
        "pos_title": pydash.get(data, "agendaLegPosition[0].postitledesc", None),
        "pos_num": pydash.get(data, "agendaLegPosition[0].posnumtext", None),
        "org": pydash.get(data, "agendaLegPosition[0].posorgshortdesc", None),
        "eta": pydash.get(data, "ailetadate", None),
        "ted": pydash.get(data, "ailetdtedsepdate", None),
        "tod": pydash.get(data, "ailtodothertext", None),
        "grade": pydash.get(data, "agendaLegPosition[0].posgradecode", None),
        "action": pydash.get(data, "latabbrdesctext", None),

        "travel": pydash.get(data, "travel", None), # TODO - get this text
    }

# aia = agenda item assignment
def fsbid_aia_to_talentmap_aia(data):

    return {
        "id": pydash.get(data, "asgdasgseqnum", None),
        "pos_title": pydash.get(data, "position[0].postitledesc", None),
        "pos_num": pydash.get(data, "position[0].posnumtext", None),
        "org": pydash.get(data, "position[0].posorgshortdesc", None),
        "eta": pydash.get(data, "asgdetadate", None),
        "ted": pydash.get(data, "asgdetdteddate", None),
        "tod": pydash.get(data, "asgdtoddesctext", None),
        "grade": pydash.get(data, "position[0].posgradecode", None),
    }