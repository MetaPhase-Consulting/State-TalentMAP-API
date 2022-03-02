import logging
import jwt
import pydash
import re
import maya
import csv
from datetime import datetime
from urllib.parse import urlencode, quote
from functools import partial

from django.utils.encoding import smart_str
from django.conf import settings
from django.http import HttpResponse

from talentmap_api.fsbid.services import common as services


PERSON_API_ROOT = settings.PERSON_API_URL
API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def get_agenda_employees(query, jwt_token=None, host=None):
    '''
    Get employees
    '''
    from talentmap_api.fsbid.services.cdo import cdo
    try:
        cdos = list(cdo(jwt_token))
    except:
        cdos = []

    args = {
        "uri": "v1/tm-persons",
        "query": query,
        "query_mapping_function": convert_agenda_employees_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_agenda_employee_to_talentmap_agenda_employee, cdos=cdos),
        "count_function": get_agenda_employees_count,
        "base_url": '',
        "host": host,
        "use_post": False,
    }

    agenda_employees = services.send_get_request(
        **args
    )

    return agenda_employees


def get_agenda_employees_count(query, jwt_token, host=None, use_post=False):
    '''
    Get total number of employees for agenda search
    '''
    args = {
        "uri": "v1/tm-persons",
        "query": query,
        "query_mapping_function": convert_agenda_employees_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "is_template": True,
    }
    return services.send_count_request(**args)


def get_agenda_employees_csv(query, jwt_token, rl_cd, host=None):
    from talentmap_api.fsbid.services.common import send_get_csv_request
    from talentmap_api.fsbid.services.cdo import cdo
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    try:
        cdos = list(cdo(jwt_token))
    except:
        cdos = []
    args = {
        "uri": "v1/tm-persons",
        "query": query,
        "query_mapping_function": convert_agenda_employees_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_agenda_employee_to_talentmap_agenda_employee, cdos=cdos),
        "base_url": API_ROOT,
        "host": host,
        "use_post": False,
    }

    data = send_get_csv_request(**args)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=agenda_employees_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Employee ID"),
        smart_str(u"CDO"),
        smart_str(u"Current Organization"),
        smart_str(u"TED"),
        smart_str(u"Handshake Organization"),
        smart_str(u"Panel Meeting Date"),
        smart_str(u"Agenda Status"),
    ])

    for record in data:
        fallback = 'None listed'
        try:
            ted = smart_str(maya.parse(record["currentAssignment"]["TED"]).datetime().strftime('%m/%d/%Y'))
        except:
            ted = fallback
        try:
            panelMeetingDate = smart_str(maya.parse(record["agenda"]["panelDate"]).datetime().strftime('%m/%d/%Y'))
        except:
            panelMeetingDate = fallback
        writer.writerow([
            smart_str(pydash.get(record, 'person.fullName')),
            smart_str("=\"%s\"" % pydash.get(record, "person.employeeID")),
            smart_str(pydash.get(record, 'person.cdo.name') or fallback),
            smart_str(pydash.get(record, 'currentAssignment.orgDescription') or fallback),
            smart_str(ted),
            smart_str(pydash.get(record, 'handshake.orgDescription') or fallback),
            smart_str(panelMeetingDate),
            smart_str(pydash.get(record, 'agenda.status') or fallback),
        ])
    return response


def convert_agenda_employees_query(query):
    '''
    Convert TalentMAP filters into FSBid filters
    '''
    qFilterValue = query.get("q", None)
    qFilterKey = ''
    qComparator = 'eq'
    if qFilterValue:
        # employee IDs can contain letters, and names can contain numbers. This does a best guess at the user's intent
        if len(''.join(re.findall('[0-9]+', qFilterValue))) > 2:
            qFilterKey = 'tmperpertexternalid'
        else:
            qFilterKey = 'tmperperfullname'
            qComparator = 'contains'
            qFilterValue = qFilterValue.upper()
    
    tedStart = query.get("ted-start")
    tedEnd = query.get("ted-end")
    
    filters = [
        { "key": "tmpercurrentbureaucode", "comparator": "IN", "value": query.get("current-bureaus", None) },
        { "key": "tmperhsbureaucode", "comparator": "IN", "value": query.get("handshake-bureaus", None) },
        { "key": "tmpercurrentorgcode", "comparator": "IN", "value": query.get("current-organizations", None) },
        { "key": "tmperhsorgcode", "comparator": "IN", "value": query.get("handshake-organizations", None) },
        { "key": "tmpercdoid", "comparator": "IN", "value": query.get("cdos", None) },
        { "key": "tmperperscode", "comparator": "IN", "value": "S,L,A,P,U" },
    ]

    if query.get("handshake", None):
        hsObj = { "key": "tmperhsind", "comparator": "IN" }
        hs = query.get("handshake", None)
        if hs == 'Y':
            hsObj['value'] = 'HS'
            filters.append(hsObj)
        elif hs == 'N':
            hsObj['comparator'] = 'EQ'
            hsObj['value'] = 'null'
            filters.append(hsObj)

    try:
        if tedStart and tedEnd:
            startVal = maya.parse(tedStart).datetime().strftime("%Y-%m-%d")
            endVal = maya.parse(tedEnd).datetime().strftime("%Y-%m-%d")
            filters.append({ "key": "tmpercurrentted", "comparator": "GTEQ", "value": startVal, "isDate": True })
            filters.append({ "key": "tmpercurrentted", "comparator": "LTEQ", "value": endVal, "isDate": True })
    except:
        logger.info(f"Invalid date {tedStart} or {tedEnd} could not be parsed.")

    filters = pydash.filter_(filters, lambda o: o["value"] != None)

    filters = pydash.map_(filters, lambda x: services.convert_to_fsbid_ql(x["key"], x["value"], x["comparator"], pydash.get(x, "isDate")))

    if qFilterKey and qFilterValue:
        filters.append(services.convert_to_fsbid_ql(qFilterKey, qFilterValue, qComparator))

    values = {
        # Pagination
        "rp.pageNum": query.get("page", 1),
        "rp.pageRows": query.get("limit", 50),
        "rp.orderBy": services.sorting_values(query.get("ordering", "agenda_employee_fullname")),
        "rp.filter": filters,
    }
    if query.get("getCount") == 'true':
        values["rp.pageNum"] = 0
        values["rp.pageRows"] = 0
        values["rp.columns"] = "ROWCOUNT"

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_agenda_employee_to_talentmap_agenda_employee(data, cdos=[]):
    '''
    Maps FSBid response to expected TalentMAP response
    '''
    firstN = data.get('perpiifirstname', '')
    lastN = data.get('perpiilastname', '')
    initials = f"{firstN[0] if firstN else ''}{lastN[0] if lastN else ''}"
    fullName = data.get("perpiifullname", "")
    if pydash.ends_with(fullName, "NMN"):
        fullName = fullName.rstrip(" NMN")
    if pydash.ends_with(fullName, "Nmn"):
        fullName = fullName.rstrip(" Nmn")
    cdo = None
    if pydash.get(data, 'cdo[0].echruid'):
        hru_id = pydash.get(data, 'cdo[0].echruid')
        cdoObj = pydash.find(cdos, lambda x: pydash.get(x, 'id') == hru_id)
        cdo = cdoObj
    return {
        "person": {
            "fullName": fullName,
            "perdet": data.get("perdetseqnum", ""),
            "employeeID": data.get("pertexternalid", ""),
            "initials": initials,
            "cdo": cdo,
        },
        "currentAssignment": {
            "TED": pydash.get(data, "currentAssignment[0].asgdetdteddate", None),
            "orgDescription": pydash.get(data, "currentAssignment[0].position[0].posorgshortdesc", None),
        },
        "hsAssignment": {
            "orgDescription": pydash.get(data, "handshake[0].posorgshortdesc", None),
        },
        "agenda": {
            "panelDate": pydash.get(data, "latestAgendaItem[0].panels[0].pmddttm", None),
            "status": pydash.get(data, "latestAgendaItem[0].aisdesctext", None),
        }
    }


@staticmethod
def fsbid_person_current_organization_to_talentmap(data):
    return {
        "code": data.get("tmpercurrentorgcode", None),
        "name": data.get("tmpercurrentorgdesc", None),
    }


@staticmethod
def fsbid_person_handshake_organization_to_talentmap(data):
    return {
        "code": data.get("tmperhsorgcode", None),
        "name": data.get("tmperhsorgdesc", None),
    }


@staticmethod
def fsbid_person_current_bureau_to_talentmap(data):
    return {
        "code": data.get("tmpercurrentbureaucode", None),
        "name": data.get("tmpercurrentbureaudesc", None),
    }


@staticmethod
def fsbid_person_handshake_bureau_to_talentmap(data):
    return {
        "code": data.get("tmperhsbureaucode", None),
        "name": data.get("tmperhsbureaudesc", None),
    }
