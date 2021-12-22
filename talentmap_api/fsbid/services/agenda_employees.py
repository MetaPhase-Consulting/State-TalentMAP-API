import logging
import jwt
import pydash
from urllib.parse import urlencode, quote

from django.conf import settings

from talentmap_api.fsbid.services import common as services


PERSON_API_ROOT = settings.PERSON_API_URL

logger = logging.getLogger(__name__)


def get_agenda_employees(query, jwt_token=None):
    '''
    Get employees
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_agenda_employee_to_talentmap_agenda_employee,
        "count_function": get_agenda_employees_count,
        "base_url": '',
        "host": None,
        "api_root": PERSON_API_ROOT,
        "use_post": False,
    }

    agenda_item = services.send_get_request(
        **args
    )

    return agenda_item

def get_agenda_employees_count(query, jwt_token, host=None, use_post=False):
    '''
    Get total number of employees for agenda search
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_employees_query,
        "jwt_token": jwt_token,
        "host": host,
        "api_root": PERSON_API_ROOT,
        "use_post": False,
    }
    return services.send_count_request(**args)

def convert_agenda_employees_query(query):
    '''
    Convert TalentMAP filters into FSBid filters
    '''
    values = {
        # Pagination
        "page_index": int(query.get("page", 1)),
        "page_size": query.get("limit", 1000),
        "order_by": query.get("ordering", None), # TODO - use services.sorting_values

        "filter": services.convert_to_fsbid_ql('pertexternalid', query.get("q", None)),
        # services.convert_to_fsbid_ql('perdetseqnum', query.get("q", None)),
        # services.convert_to_fsbid_ql('perpiilastname', query.get("q", None)), TODO - passing multiples values
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_agenda_employee_to_talentmap_agenda_employee(data):
    '''
    Maps FSBid response to expected TalentMAP response
    '''
    persons = data.get('persons', {})
    return {
        "persons": {
            "lastName": persons.get("perpiilastname", ""),
            "firstName": persons.get("perpiifirstname", ""),
            "middleName": persons.get("perpiimiddlename", ""),
            "suffix": persons.get("perpiisuffixname", ""),
            "fullName": persons.get("perpiifullname", ""),
            "perdet": persons.get("perdetseqnum", ""),
            "employeeID": persons.get("pertexttcode", ""),
            # persons.get("perpiiseqnum", ""),
            # persons.get("perdetperscode", ""),
            # persons.get("pertexternalid", ""),
            # persons.get("perdetorgcode", ""),
            # persons.get("pertcurrentind", ""),
        },
    }
