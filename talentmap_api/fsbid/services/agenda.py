import jwt
import logging
import pydash
from functools import partial
from urllib.parse import urlencode, quote

from django.conf import settings
from django.http import QueryDict

from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import ensure_date, sort_legs

AGENDA_API_ROOT = settings.AGENDA_API_URL

logger = logging.getLogger(__name__)


def get_single_agenda_item(jwt_token=None, pk=None):
    '''
    Get single agenda item
    '''
    args = {
        "uri": "",
        "query": {'aiseqnum': pk},
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "count_function": None,
        "base_url": "/api/v1/fsbid/agenda/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_item = services.send_get_request(
        **args
    )

    return pydash.get(agenda_item, 'results[0]') or None


def get_agenda_items(jwt_token=None, query={}, host=None):
    '''
    Get agenda items
    '''
    from talentmap_api.fsbid.services.agenda_employees import get_agenda_employees
    remarks = get_agenda_remarks({}, jwt_token)
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_single_agenda_item_to_talentmap_single_agenda_item, remarks=remarks),
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "host": host,
        "use_post": False,
        "api_root": AGENDA_API_ROOT,
    }

    agenda_items = services.send_get_request(
        **args
    )

    employeeQuery = QueryDict(f"limit=1&page=1&perdet={query.get('perdet', None)}")
    employee = get_agenda_employees(employeeQuery, jwt_token, host)
    return {
        "employee": employee,
        "results": agenda_items,
    }


def create_agenda(query={}, jwt_token=None, host=None):
    '''
    Create agenda
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    query['hru_id'] = hru_id
    print('1. query ---------------------------------------------------', query)
    logger.info('1. query ---------------------------------------------------', query)
    print('2. calling pmi ---------------------------------------------------')
    logger.info('2. calling pmi ---------------------------------------------------')
    panel_meeting_item = create_panel_meeting_item(query, jwt_token)
    pmi_seq_num = pydash.get(panel_meeting_item, '[0].pmi_seq_num')
    if pmi_seq_num:
        query['pmiseqnum'] = pmi_seq_num
        print('3. calling ai ---------------------------------------------------')
        logger.info('3. calling ai ---------------------------------------------------')
        agenda_item = create_agenda_item(query, jwt_token)
        ai_seq_num = pydash.get(agenda_item, '[0].ai_seq_num')
        if ai_seq_num:
            query['aiseqnum'] = ai_seq_num
            logger.info('🥹🥹🥹if ai_seq_num: true')
            if pydash.get(query, 'agendaLegs'):
                print('4. calling ail ---------------------------------------------------')
                logger.info('4. calling ail ---------------------------------------------------')
                for x in query['agendaLegs']:
                    create_agenda_item_leg(x, query, jwt_token)
        else:
            logger.error("AI create failed")
    else:
        logger.error("PMI create failed")


def create_panel_meeting_item(query, jwt_token):
    '''
    Create PMI
    '''
    logger.info('🟣🟣🟣 in create_panel_meeting_item')
    args = {
        "uri": "v1/panels/meetingItem",
        "query": query,
        "query_mapping_function": convert_panel_meeting_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.send_fsbid_post(
        **args
    )


def create_agenda_item(query, jwt_token):
    '''
    Create AI
    '''
    logger.info('🐳🐳🐳 in create_agenda_item')
    args = {
        "uri": "v1/agendas",
        "query": query,
        "query_mapping_function": convert_create_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.send_fsbid_post(
        **args
    )


def create_agenda_item_leg(data, query, jwt_token):
    '''
    Create AIL
    '''
    logger.info('🐸🐸🐸🐸🐸🐸🐸🐸 in create_agenda_item_leg')
    aiseqnum = query["aiseqnum"]
    args = {
        "uri": f"v1/agendas/{aiseqnum}/legs",
        "query": query,
        "query_mapping_function": partial(convert_agenda_item_leg_query, leg=data),
        "jwt_token": jwt_token,
        "mapping_function": "" 
    }

    return services.send_fsbid_post(
        **args
    )


def get_agenda_item_history_csv(query, jwt_token, host, limit=None):
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "host": host,
        "use_post": False,
        "base_url": AGENDA_API_ROOT,
    }

    data = services.send_get_csv_request(
        **args
    )

    response = services.get_aih_csv(data, f"agenda_item_history_{query.get('client')}")

    return response


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
        "api_root": AGENDA_API_ROOT,
    }
    return services.send_count_request(**args)


def convert_agenda_item_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.columns": None,
        "rp.orderBy": services.sorting_values(query.get("ordering", "agenda_id")),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'aiperdetseqnum', 'val': query.get("perdet", None)},
            {'col': 'aiseqnum', 'val': query.get("aiseqnum", None)}
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_single_agenda_item_to_talentmap_single_agenda_item(data, remarks={}):
    agendaStatusAbbrev = {
        "Approved": "APR",
        "Deferred - Proposed Position": "XXX",
        "Disapproved": "DIS",
        "Deferred": "DEF",
        "Held": "HLD",
        "Move to ML/ID": "MOV",
        "Not Ready": "NR",
        "Out of Order": "OOO",
        "PIP": "PIP",
        "Ready": "RDY",
        "Withdrawn": "WDR"
    }
    legsToReturn = []
    assignment = fsbid_aia_to_talentmap_aia(
        pydash.get(data, "agendaAssignment[0]", {})
    )
    legs = (list(map(
        fsbid_legs_to_talentmap_legs, pydash.get(data, "agendaLegs", [])
    )))
    sortedLegs = sort_legs(legs)
    legsToReturn.extend([assignment])
    legsToReturn.extend(sortedLegs)
    statusFull = data.get("aisdesctext", None)

    return {
        "id": data.get("aiseqnum", None),
        "remarks": services.parse_agenda_remarks(data.get("aicombinedremarktext", ''), remarks),
        "panel_date": ensure_date(pydash.get(data, "Panel[0].pmddttm", None), utc_offset=-5),
        "status_full": statusFull,
        "status_short": agendaStatusAbbrev.get(statusFull, None),
        "perdet": data.get("aiperdetseqnum", None),

        "assignment": fsbid_aia_to_talentmap_aia(
            pydash.get(data, "agendaAssignment[0]", {})
        ),

        "legs": legsToReturn,

        "update_date": ensure_date(data.get("update_date", None), utc_offset=-5),  # TODO - find this date
        "modifier_name": data.get("aiupdateid", None),  # TODO - this is only the id
        "creator_name": data.get("aiitemcreatorid", None),  # TODO - this is only the id
    }


def fsbid_agenda_items_to_talentmap_agenda_items(data, jwt_token=None):
    ai_id = data.get("aiseqnum", None)

    agenda_item = get_single_agenda_item(jwt_token, ai_id)

    return {
        "id": data.get("aiseqnum", None),
        **agenda_item,
    }


def fsbid_legs_to_talentmap_legs(data):
    # Temporary mapping helper. FSBid will handle this
    tf_mapping = {
        "8150": "Post to Post without Home Leave (Direct Transfer)",
        "8151": "Post to Post with Home Leave",
        "8152": "Post to U.S. with Home Leave",
        "8153": "Post to U.S. without Home Leave (Direct Transfer to U.S.)",
        "8154": "Separation from the Service",
        "8155": "U.S. to Post",
        "8156": "Initial Appointment to Post from U.S.",
        "8157": "Initial Appointment to U.S.",
        "8158": "Initial Appointment from Overseas",
        "8159": "Intra U.S. (Transfer from one U.S. Location to Another U.S. Location)",
        "8160": "Round Trip Home Leave",
        "8161": "Advance Travel of Dependents",
        "8162": "Remains of Deceased Dependents",
        "8169": "SMA Travel",
    }

    def map_tf(tf=None):
        return pydash.get(tf_mapping, tf, None)

    res = {
        "id": pydash.get(data, "ailaiseqnum", None),
        "pos_title": pydash.get(data, "agendaLegPosition[0].postitledesc", None),
        "pos_num": pydash.get(data, "agendaLegPosition[0].posnumtext", None),
        "org": pydash.get(data, "agendaLegPosition[0].posorgshortdesc", None),
        "eta": pydash.get(data, "ailetadate", None),
        "ted": pydash.get(data, "ailetdtedsepdate", None),
        "tod": pydash.get(data, "ailtodothertext", None),
        "grade": pydash.get(data, "agendaLegPosition[0].posgradecode", None),
        "action": pydash.get(data, "latabbrdesctext", None),
        "travel": map_tf(pydash.get(data, "ailtfcd", None)),
    }

    # Avoid the need to do this logic on the front-end
    if res['action'] == 'Resign':
        res['pos_title'] = 'RESIGNATION'
        res['pos_num'] = 'N/A'

    if res['action'] == 'Retire':
        res['pos_title'] = 'RETIREMENT'
        res['pos_num'] = 'N/A'

    if res['action'] == 'Termination':
        res['pos_title'] = 'TERMINATION'
        res['pos_num'] = 'N/A'

    if res['action'] == 'Death in Service':
        res['pos_title'] = 'DEATH IN SERVICE'
        res['pos_num'] = 'N/A'

    # TODO - determine all edge cases for actions where there is no positions information

    return res


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


def get_agenda_statuses(query, jwt_token):
    '''
    Get agenda statuses
    '''

    args = {
        "uri": "references/statuses",
        "query": query,
        "query_mapping_function": convert_agenda_statuses_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_statuses,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_statuses = services.send_get_request(
        **args
    )

    return agenda_statuses


def convert_agenda_statuses_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def convert_panel_meeting_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    creator_id = pydash.get(query, "hru_id")
    print(type(creator_id))
    print('-----------cat------------')
    values = {
        "pmimiccode": pydash.get(query, "panelMeetingCategory") or "D",
        "pmipmseqnum": int(pydash.get(query, "panelMeetingId")),
        "pmicreateid": creator_id,
        "pmiupdateid": creator_id,
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def convert_create_agenda_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    user_id = pydash.get(query, "hru_id")
    values = {
        "aipmiseqnum": pydash.get(query, "pmiseqnum", ""),
        "aiempseqnbr": pydash.get(query, "personId", ""),
        "aiperdetseqnum": pydash.get(query, "personDetailId", ""),
        "aiaiscode": pydash.get(query, "agendaStatusCode", ""),
        "aitoddesctext": None,
        "aitodcode": None,
        "aiasgseqnum": pydash.get(query, "assignmentId", ""),
        "aiasgdrevisionnum": pydash.get(query, "assignmentVersion", ""),
        "aicombinedtodmonthsnum": None,
        "aicombinedtodothertext": None,
        "aicombinedremarktext": None,
        "aicorrectiontext": None,
        "ailabeltext": None,
        "aisorttext": None,
        "aicreateid": user_id,
        "aicreatedate": None,
        "aiupdateid": user_id,
        "aiseqnumref": None,
        "aiitemcreatorid": user_id,
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def convert_agenda_item_leg_query(query, leg={}):
    '''
    Converts TalentMap query into FSBid query
    '''
    user_id = int(pydash.get(query, "hru_id"))
    values = {
        "aillatcode": pydash.get(leg, "legActionType", ""),
        "ailtfcd": pydash.get(leg, "travelFunctionCode", ""),
        "ailcpid": int(pydash.get(leg, "cpId")) or None,
        "ailempseqnbr": int(pydash.get(query, "personId")) or None,
        "ailperdetseqnum": pydash.get(query, "persodDetailId") or None,
        "ailposseqnum": int(pydash.get(leg, "posSeqNum")) or None,
        "ailtodcode": pydash.get(leg, "tourOfDutyCode", ""),
        "ailtodmonthsnum": None,
        "ailtodothertext": None,
        "ailetadate": pydash.get(leg, "legStartDate", None),
        "ailetdtedsepdate": pydash.get(leg, "legEndDate", None),
        "aildsccd": None,
        "ailcitytext": None,
        "ailcountrystatetext": None,
        "ailusind": None,
        "ailemprequestedsepind": None,
        "ailcreateid": user_id,
        "ailupdateid": user_id,
        "ailasgseqnum": int(pydash.get(leg, "legAssignmentId")) or None,
        "ailasgdrevisionnum": int(pydash.get(leg, "legAssignmentVersion")) or None,
        "ailsepseqnum": None,
        "ailsepdrevisionnum": None,
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_to_talentmap_agenda_statuses(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'abbr_desc_text', 'desc_text']

    add_these = []

    cols_mapping = {
        'code': 'aiscode',
        'abbr_desc_text': 'aisabbrdesctext',
        'desc_text': 'aisdesctext',
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_remarks(query, jwt_token):
    '''
    Get agenda remarks
    '''
    args = {
        "uri": "references/remarks",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_remarks,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_remarks = services.send_get_request(
        **args
    )

    return agenda_remarks


def fsbid_to_talentmap_agenda_remarks(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['seq_num', 'rc_code', 'order_num', 'short_desc_text', 'mutually_exclusive_ind', 'text', 'active_ind']

    add_these = []

    cols_mapping = {
        'seq_num': 'rmrkseqnum',
        'rc_code': 'rmrkrccode',
        'order_num': 'rmrkordernum',
        'short_desc_text': 'rmrkshortdesctext',
        'mutually_exclusive_ind': 'rmrkmutuallyexclusiveind',
        'text': 'rmrktext',
        'active_ind': 'rmrkactiveind'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_remark_categories(query, jwt_token):
    '''
    Get agenda remark categories
    '''
    args = {
        "uri": "references/remark-categories",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_remark_categories,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_remark_categories = services.send_get_request(
        **args
    )

    return agenda_remark_categories


def fsbid_to_talentmap_agenda_remark_categories(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'desc_text']

    add_these = []

    cols_mapping = {
        'code': 'rccode',
        'desc_text': 'rcdesctext'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_leg_action_types(query, jwt_token):
    '''
    Get agenda leg-action-types
    '''
    args = {
        "uri": "references/leg-action-types",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_leg_action_types,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_leg_action_types = services.send_get_request(
        **args
    )

    return agenda_leg_action_types


def fsbid_to_talentmap_agenda_leg_action_types(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'abbr_desc_text', 'desc_text']

    add_these = []

    cols_mapping = {
        'code': 'latcode',
        'abbr_desc_text': 'latabbrdesctext',
        'desc_text': 'latdesctext'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)
