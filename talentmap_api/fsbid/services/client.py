import csv
import logging
from copy import deepcopy
from datetime import datetime
from urllib.parse import urlencode, quote
from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
import jwt
import pydash

from talentmap_api.fsbid.services import common as services
import talentmap_api.fsbid.services.cdo as cdo_services
import talentmap_api.fsbid.services.available_positions as services_ap
from talentmap_api.common.common_helpers import combine_pp_grade, ensure_date
from talentmap_api.fsbid.requests import requests


SECREF_ROOT = settings.SECREF_URL
CLIENTS_ROOT = settings.CLIENTS_API_URL
CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL

logger = logging.getLogger(__name__)


def get_user_information(jwt_token, perdet_seq_num):
    '''
    Gets the office_phone and office_address for the employee
    '''
    url = f"{SECREF_ROOT}/user?request_params.perdet_seq_num={perdet_seq_num}"
    user = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    user = next(iter(user.get('Data', [])), {})
    try:
        return {
            "office_address": pydash.get(user, 'gal_address_text'),
            "office_phone": pydash.get(user, 'gal_phone_nbr_text'),
            "email": pydash.get(user, 'gal_smtp_email_address_text'),
            "hru_id": pydash.get(user, 'hru_id'),
        }
    except:
        return {}


def client(jwt_token, query, host=None):
    '''
    Get Clients by CDO
    '''
    from talentmap_api.fsbid.services.common import send_get_request
    try:
        response = send_get_request(
            "",
            query,
            convert_client_query,
            jwt_token,
            fsbid_clients_to_talentmap_clients,
            get_clients_count,
            "/api/v2/clients/",
            host,
            CLIENTS_ROOT_V2,
        )
    except Exception as e:
        logger.error(f"Error getting clients: {e}\n")
        return None

    return response

def get_client_perdets(jwt_token, query, host=None):
    '''
    Get Bidder Type
    '''
    args = {
        "proc_name": "prc_lst_cdo_wl_clients",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT99_PJD",
        "request_mapping_function": get_client_perdets_req_mapping,
        "response_mapping_function": get_client_perdets_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def get_client_perdets_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "PV_SUBTRAN_I": "",
        "PV_CDO_WL_CODE_I": convert_bidder_type_query(request),
        "PV_CDO_HRU_ID_I": request.get("hru_id__in"),
        "PV_CDO_BSN_ID_I": request.get("bid_seasons") 
    }

def get_client_perdets_res_mapping(data):
    if data is None and data['PV_RETURN_CODE_O'] is not 0:
        logger.error('FSBid call for client perdets failed.')
        return None
    return [item['PER_SEQ_NUM1'] for item in data['PV_DETAIL_O']]

def get_extra_client_data(jwt_token, query, host=None):
    '''
    Get Extra Client Data
    '''
    args = {
        "proc_name": "prc_lst_all_clients",
        "package_name": "pkg_webapi_wrap",
        "request_mapping_function": get_extra_client_data_req_mapping,
        "response_mapping_function": get_extra_client_data_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def get_extra_client_data_req_mapping(request):
    return {
        'pv_api_version_i':'',
        'pv_cdo_hru_i': request.get("hru_id__in"),
    }

def get_extra_client_data_res_mapping(data):
    if data is None and data['PV_RETURN_CODE_O'] is not 0:
        logger.error('FSBid call for extra client data failed.')
        return None
    return data['PV_DETAIL_O']



def convert_bidder_type_query(type):
    type_mapping = {
        'noBids': 'NB',
        'noPanel': 'NP',
        'handshake': 'HS',
        'eligible_bidders': 'EB',
        'cusp_bidders': 'CU',
        'languages': 'LA',
        'separations': 'SB',
        'classification': 'BC',
        'panel_clients': 'PC',
    }
    
    for key, code in type_mapping.items():
        if type.get(key):
            return code
    return None

def update_client(data, jwt_token, host=None):
    '''
    Update current client
    '''
    args = {
        "proc_name": 'prc_mod_alt_email_bscc',
        "package_name": 'Pkg_Wrap_dev',
        "request_mapping_function": update_client_req_mapping,
        "response_mapping_function": update_user_client_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def update_client_req_mapping(request):
    bidSeasons = ",".join([str(x) for x in request.get("bid_seasons")])
    return {
        "PV_AD_ID_I":"",
        "pv_subtran_i":0,
        "PV_WL_CODE_I":"",
        "pv_hru_id_i": request.get("hru_id"),
        "PV_PER_SEQ_NUM_I": request.get("per_seq_number"),
        "PV_BSN_ID_I": bidSeasons,
        "PV_BSCC_COMMENT_TEXT_I": request.get("comments"),
        "pv_cae_email_address_text_i": request.get("email"),
    }

def update_user_client_res_mapping(data):
    if data is None or (data['PV_RETURN_CODE_O'] and data['PV_RETURN_CODE_O'] is not 0):
        logger.error('FSBid call for Updating current client failed.')
        return None
    
    return data
 
def get_clients_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    from talentmap_api.fsbid.services.common import send_count_request
    try:
        return send_count_request("", query, convert_client_count_query, jwt_token, host, CLIENTS_ROOT_V2)
    except Exception as e:
        logger.error(f"Error getting clients count: {e}\n")
        return None


def client_suggestions(jwt_token, perdet_seq_num):
    '''
    Get a suggestion for a client
    '''

    # if less than LOW, try broader query
    LOW = 5
    # but also don't go too high
    HIGH = 100
    # but going over HIGH is preferred over FLOOR
    FLOOR = 0

    try: 
        CLIENT = single_client(jwt_token, perdet_seq_num)
        grade = CLIENT.get("grade")
        skills = CLIENT.get("skills")
        skills = deepcopy(skills)
        mappedSkills = ','.join([str(x.get("code")) for x in skills])
    except Exception as e:
        logger.error(f"Error getting client suggestions: {e}\n")
        return None

    values = {
        "position__grade__code__in": grade,
        "position__skill__code__in": mappedSkills,
    }

    # Dictionary for the next grade "up"
    nextGrades = {
        "08": "07",
        "07": "06",
        "06": "05",
        "05": "04",
        "04": "03",
        "02": "01",
    }

    try:
        count = services_ap.get_available_positions_count(values, jwt_token)
        count = int(count.get("count"))
    except Exception as e:
        logger.error(f"Error getting client suggestions count: {e}\n")
        return None

    # If we get too few results, try a broader query
    if count < LOW and nextGrades.get(grade) is not None:
        nextGrade = nextGrades.get(grade)
        values2 = deepcopy(values)
        values2["position__grade__code__in"] = f"{grade},{nextGrade}"
        count2 = services_ap.get_available_positions_count(values2, jwt_token)
        count2 = int(count2.get("count"))
        # Only use our broader query if the first one <= FLOOR OR the second < HIGH, and the counts don't match
        if (count <= FLOOR or count2 < HIGH) and count != count2:
            values = values2

    # Finally, return the query
    return values


def single_client(jwt_token, perdet_seq_num, host=None):
    '''
    Get a single client for a CDO
    '''
    from talentmap_api.fsbid.services.common import send_get_request
    
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')

    query = {
        "ad_id": ad_id,
        "perdet_seq_num": perdet_seq_num,
        "currentAssignmentOnly": "false",
    }

    try:
        responseAllAssignments = send_get_request(
            "",
            query,
            convert_client_query,
            jwt_token,
            fsbid_clients_to_talentmap_clients,
            get_clients_count,
            "/api/v2/clients/",
            host,
            CLIENTS_ROOT_V2,
        )
    except Exception as e:
        logger.error(f"Error getting responseAllAssignments: {e}\n")
        return None
    
    query["currentAssignmentOnly"] = "true"

    try:
        responseCurrentAssignment = send_get_request(
            "",
            query,
            convert_client_query,
            jwt_token,
            fsbid_clients_to_talentmap_clients,
            get_clients_count,
            "/api/v2/clients/",
            host,
            CLIENTS_ROOT_V2,
        )
    except Exception as e:
        logger.error(f"Error getting responseCurrentAssignment: {e}\n")
        return None

    cdo = cdo_services.single_cdo(jwt_token, perdet_seq_num)
    user_info = get_user_information(jwt_token, perdet_seq_num)
    
    try:
        CLIENT = list(responseAllAssignments['results'])[0]
        CLIENT['cdo'] = cdo
        CLIENT['user_info'] = user_info
        CLIENT['current_assignment'] = list(responseCurrentAssignment['results'])[0].get('current_assignment', {})
        return CLIENT
    except IndexError:
        pass


def get_client_csv(query, jwt_token, rl_cd, host=None):
    """
    Create a CSV containing the clients' information
    """
    from talentmap_api.fsbid.services.common import send_get_csv_request
    
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')

    try:
        data = send_get_csv_request(
            "",
            query,
            convert_client_query,
            jwt_token,
            fsbid_clients_to_talentmap_clients_for_csv,
            CLIENTS_ROOT_V2,
            host,
            ad_id
        )
        logger.info(f"Got {len(data)} records for CSV\n")
        logger.info(f"Data: {data}\n")
    except Exception as e:
        logger.error(f"Error getting client CSV: {e}\n")
        return None

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=clients_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Email"),
        smart_str(u"Skill"),
        smart_str(u"PP/Grade"),
        smart_str(u"CDO"),
        smart_str(u"Employee ID"),
        smart_str(u"Position Code"),
        smart_str(u"Location (Org)"),
        smart_str(u"Languages"),
        smart_str(u"TED"),
        smart_str(u"Status"),
    ])

    try:
        logger.info(f"Writing {len(data)} records to CSV\n\n")
        for record in data:
            email_response = get_user_information(jwt_token, record['id'])
            email = pydash.get(email_response, 'email') or 'None listed'
            writer.writerow([
                smart_str(record["name"]),
                email,
                smart_str(record["skills"]),
                smart_str("=\"%s\"" % record["combined_pp_grade"]),
                smart_str("=\"%s\"" % record["cdo"]),
                smart_str("=\"%s\"" % record["employee_id"]),
                smart_str("=\"%s\"" % record["position_code"]),
                smart_str("=\"%s\"" % record["location"]),
                smart_str("=\"%s\"" % record["languages"]),
                smart_str("=\"%s\"" % record["ted"]),
                smart_str("=\"%s\"" % record["status"]),
            ])
    except Exception as e:
        logger.error(f"Didn't write to CSV correctly. Woops\n FIX IT\n")
        logger.error(f"exception caught: {e}\n")
        return None

    return response


def fsbid_clients_to_talentmap_clients(data):
    employee = data.get('employee', None)
    current_assignment = None
    assignments = None
    position = None
    location = {}

    if employee is not None:
        current_assignment = employee.get('currentAssignment', None)

    if employee.get('assignment', None) is not None:
        assignments = employee.get('assignment', None)
        # handle if array
        if type(assignments) is type([]) and list(assignments):
            current_assignment = list(assignments)[0]
        # handle if object
        if type(assignments) is type(dict()):
            current_assignment = assignments
            # remove current prefix
            if assignments.get('currentPosition', None) is not None:
                assignments['position'] = assignments['currentPosition']
                assignments['position']['location'] = assignments['currentPosition']['currentLocation']
                assignments = [].append(assignments)

    if current_assignment is not None:
        # handle if object
        if current_assignment.get('currentPosition', None) is not None:
            position = current_assignment.get('currentPosition', None)
        # handle if array
        if current_assignment.get('position', None) is not None:
            position = current_assignment.get('position', None)

    if position is not None:
        # handle if object
        if position.get('currentLocation', None) is not None:
            location = position.get('currentLocation', {})
        # handle if array
        if position.get('location', None) is not None:
            location = position.get('location', {})

    if current_assignment and current_assignment.get('currentPosition', None) is not None:
        # remove current prefix
        current_assignment['position'] = current_assignment['currentPosition']
        current_assignment['position']['location'] = current_assignment['position']['currentLocation']

    # first object in array, mapped
    try:
        current_assignment = fsbid_assignments_to_tmap(current_assignment)[0]
    except:
        current_assignment = {}

    initials = None
    try:
        initials = employee['per_first_name'][:1] + employee['per_last_name'][:1]
    except:
        initials = None

    middle_name = get_middle_name(employee)
    suffix_name = f" {employee['per_suffix_name']}" if pydash.get(employee, 'per_suffix_name') else ''

    pp = employee.get("per_pay_plan_code")
    grade = employee.get("per_grade_code")
    combined_pp_grade = combine_pp_grade(pp, grade)
    altEmail = data.get("alternateEmails", None)
    comment = data.get("bidSeasonComments", None)
    alternative_email = None
    comments = None

    if altEmail is not None:
        alternative_email = altEmail.get('caeemailaddresstext', None)

    if comment is not None:
        comments = comment.get('bscccommenttext', None)

    return {
        "id": str(employee.get("pert_external_id", None)),
        "hru_id": data.get("hru_id", None),
        "per_seq_num": employee.get("per_seq_num", None),
        "name": f"{employee.get('per_first_name', None)} {middle_name['full']}{employee.get('per_last_name', None)}{suffix_name}",
        "shortened_name": f"{employee.get('per_last_name', None)}{suffix_name}, {employee.get('per_first_name', None)} {middle_name['initial']}",
        "initials": initials,
        "perdet_seq_number": str(int(employee.get("perdet_seq_num", None))),
        "pay_plan": pp,
        "alt_email": alternative_email,
        "comments": comments,
        "grade": grade,
        "combined_pp_grade": combined_pp_grade,
        "skills": map_skill_codes(employee),
        "employee_id": str(employee.get("pert_external_id", None)),
        "role_code": data.get("rl_cd", None),
        "pos_location": map_location(location),
        # not exposed in FSBid yet
        # "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        # "noPanel": fsbid_no_successful_panel_to_tmap(data.get("no_successful_panel")),
        # "noBids": fsbid_no_bids_to_tmap(data.get("no_bids")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications") or []),
        "languages": fsbid_languages_to_tmap(data.get("languages", []) or []),
        "cdos": data.get("cdos") or [],
        "current_assignment": current_assignment,
        "assignments": fsbid_assignments_to_tmap(assignments),
    }


def parse_date_string(date_string):
    # Try to parse the date string as an ISO 8601 format with timezone offset
    # Ex: '2023-07-01T00:00:00-04:00'
    try:
        if date_string[-6] in ['+', '-']:
            date_string = date_string[:-6]  # Remove timezone information for parsing
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

        # Try to handle the format with 'Z' for UTC
        # Ex: '2024-06-27T19:39:28.044Z'
        elif date_string.endswith('Z'):
            date_string = date_string[:-1]  # Remove the 'Z'
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            return date_string
    except ValueError:
        logger.error(f"Error parsing this date string: {date_string}\n")
        return None


def format_date_string(date_string):
    """Formats a date string to MM/DD/YYYY"""
    if date_string == '' or date_string is None or len(date_string) == 10:
        return date_string
    try:
        dt = parse_date_string(date_string)
    except ValueError:
        logger.error(f"Error formatting this date string: {date_string}\n")
        return date_string

    formatted_date = dt.strftime('%m/%d/%Y')
    return formatted_date


def fsbid_clients_to_talentmap_clients_for_csv(data):

    employee = data.get('employee', None)
    current_assignment = employee.get('currentAssignment', None)
    position = None
    pos_location = None
    ted = None
    position_code = None
    status = None
    middle_name = get_middle_name(employee)
    pp = employee.get("per_pay_plan_code")
    grade = employee.get("per_grade_code")
    combined_pp_grade = combine_pp_grade(pp, grade)

    if current_assignment is not None:
        position = current_assignment.get('currentPosition', None)
        ted = format_date_string(current_assignment.get("asgd_etd_ted_date", None))
        position_code = current_assignment.get("pos_seq_num", None)
        status = current_assignment.get("asgs_code", None)
        if position is not None:
            pos_location = map_location(position.get("currentLocation", None))

    suffix_name = f" {employee['per_suffix_name']}" if pydash.get(employee, 'per_suffix_name') else ''
    combined_location = f"{pos_location} ({position.get('pos_org_short_desc', None)})" if position is not None else pos_location
    cdo = data.get('cdos', None)
    
    try:
        client = {
            "id": employee.get("perdet_seq_num", None),
            "name": f"{employee.get('per_last_name', None)}{suffix_name}, {employee.get('per_first_name', None)} {middle_name['full']}",
            "grade": employee.get("per_grade_code", None),
            "skills": ' , '.join(map_skill_codes_for_csv(employee)),
            "employee_id": employee.get("pert_external_id", None),
            "role_code": data.get("rl_cd", None),
            "location": combined_location,
            "ted": ted,
            "status": status,
            "position_code": position_code,
            "combined_pp_grade": combined_pp_grade,
            "cdo": cdo[0].get('cdo_fullname', None),
            "languages": fsbid_language_only_to_tmap(data.get("languages") or []),
            "classifications": fsbid_classifications_to_tmap(employee.get("classifications", []))
        }
    except Exception as e:
        logger.error(f"Error mapping client for CSV: {e}\n")
        return None

    return client


def get_middle_name(employee, prop='per_middle_name'):
    """
    Parsing clients' middle name
    """

    try:
        middle_name = employee.get(prop, None) or ''

        middle_initial = ''

        if middle_name == 'NMN':
            middle_name = ''

        if middle_name:
            middle_name = middle_name + ' '
            middle_initial = middle_name[:1] + ' '
            
        return {"full": middle_name, "initial": middle_initial}
    except Exception as e:
        logger.error(f"Error getting middle name: {e}\n")
        return ''


def hru_id_filter(query):
    from talentmap_api.fsbid.services.common import convert_multi_value
    results = []
    hru_id = query.get("hru_id", None)
    results += [hru_id] if hru_id is not None else []
    hru_ids = convert_multi_value(query.get("hru_id__in", None))
    results += hru_ids if hru_ids is not None else []
    return results if len(results) > 0 else None


def convert_client_query(query, isCount=None):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the client search filter naming
    '''
    from talentmap_api.fsbid.services.common import sorting_values, convert_multi_value
    try:
        values = {
            "request_params.hru_id": hru_id_filter(query),
            "request_params.rl_cd": query.get("rl_cd", None),
            "request_params.ad_id": query.get("ad_id", None),
            "request_params.order_by": sorting_values(query.get("ordering", None)),
            "request_params.freeText": query.get("q", None),
            "request_params.bsn_id": convert_multi_value(query.get("bid_seasons")),
            "request_params.hs_cd": tmap_handshake_to_fsbid(query.get('hasHandshake', None)),
            "request_params.no_successful_panel": tmap_no_successful_panel_to_fsbid(query.get('noPanel', None)),
            "request_params.no_bids": tmap_no_bids_to_fsbid(query.get('noBids', None)),
            "request_params.page_index": int(query.get("page", 1)),
            "request_params.page_size": query.get("limit", 25),
            "request_params.currentAssignmentOnly": query.get("currentAssignmentOnly", 'true'),
            "request_params.get_count": query.get("getCount", 'false'),
            "request_params.perdet_seq_num": query.get("perdet_seq_num", None),
        }
        if isCount:
            values['request_params.page_size'] = None
        return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
    except Exception as e:
        logger.error(f"Error converting client query: {e}\n")
        return None


def convert_client_count_query(query):
    try:
        return convert_client_query(query, True)
    except Exception as e:
        logger.error(f"Error converting client count query: {e}\n")
        return None


def map_skill_codes_for_csv(data, prefix='per'):
    """
    Mapping skill codes for csv export
    """
    skills = []
    try:
        for i in range(1, 4):
            index = f'_{i}'
            if i == 1:
                index = ''
            code = data.get(f'{prefix}_skill{index}_code', None)
            desc = data.get(f'{prefix}_skill{index}_code_desc', None)
            skill = f'({code}) {desc}'
            if code is None:
                continue
            skills.append(skill)

        return filter(lambda x: x is not None, skills)
    except Exception as e:
        logger.error(f"Error mapping skill codes for CSV in map_skill_codes_for_csv:\n {e}\n")
        return None


def map_skill_codes(data):
    skills = []
    try:
        for i in range(1, 4):
            index = f'_{i}'
            if i == 1:
                index = ''
            code = pydash.get(data, f'per_skill{index}_code', None)
            desc = pydash.get(data, f'per_skill{index}_code_desc', None) # Not coming through with /Persons
            skills.append({'code': code, 'description': desc})

        return filter(lambda x: x.get('code', None) is not None, skills)
    except Exception as e:
        logger.error(f"Error mapping skill codes: {e}\n")
        return None


def map_skill_codes_additional(skills, employeeSkills):
    employeeCodesAdd = []
    try:
        for w in employeeSkills:
            foundSkill = [a for a in skills if a['skl_code'] == w['code']]
            # some times, the user's skill is not in the full /skillCodes list
            if foundSkill:
                foundSkill = foundSkill[0]
                cone = foundSkill['jc_nm_txt']
                foundSkillsByCone = [b for b in skills if b['jc_nm_txt'] == cone]
                for x in foundSkillsByCone:
                    employeeCodesAdd.append(x['skl_code'])
    except Exception as e:
        logger.error(f"Error in map_skill_codes_additional: {e}\n")
        logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
    return set(employeeCodesAdd)


def map_location(location):

    try:
        city = location.get('city')
        country = location.get('country')
        state = location.get('state')
        result = city
    except Exception as e:
        logger.error(f"Error extracting location pieces from argument: {e}\n")
        return None
    
    if country and country.strip():
        result = f"{city}, {country}"

    if state and state.strip():
        result = f"{city}, {state}"
    
    return result


def fsbid_handshake_to_tmap(hs):
    # Maps FSBid Y/N value for handshakes to expected TMap Front end response for handshake
    try:
        fsbid_dictionary = {
            "Y": True,
            "N": False
        }
        return fsbid_dictionary.get(hs, None)
    except Exception as e:
        logger.error(f"Error in fsbid_handskake: {e}\n")
        return None


def tmap_handshake_to_fsbid(hs):
    # Maps TMap true/false value to acceptable fsbid api params for handshake
    try:
        tmap_dictionary = {
            "true": "Y",
            "false": "N"
        }
        return tmap_dictionary.get(hs, None)
    except Exception as e:
        logger.error(f"Error in tmap_handshake_to_fsbid: {e}\n")
        return None


def fsbid_no_successful_panel_to_tmap(panel):
    try:
        fsbid_dictionary = {
            "Y": True,
            "N": False
        }
        return fsbid_dictionary.get(panel, None)
    except Exception as e:
        logger.error(f"Error in fsbid_no_successful_panel_to_tmap: {e}\n")
        return None


def tmap_no_successful_panel_to_fsbid(panel):
    try:
        tmap_dictionary = {
            "true": "Y",
            "false": "N"
        }
        return tmap_dictionary.get(panel, None)
    except Exception as e:  
        logger.error(f"Error in tmap_no_successful_panel_to_fsbid: {e}\n")
        return None


def tmap_cusp_and_eligible_bidders_to_fsbid(bidder):
    tmap_dictionary = {
        "true": "Y",
    }
    return tmap_dictionary.get(bidder, None)

def fsbid_no_bids_to_tmap(bids):
    try:
        fsbid_dictionary = {
            "Y": True,
            "N": False
        }
        return fsbid_dictionary.get(bids, None)
    except Exception as e: 
        logger.error(f"Error in fsbid_no_bids_to_tmap: {e}\n")
        return None


def tmap_no_bids_to_fsbid(bids):
    try:
        tmap_dictionary = {
            "true": "Y",
            "false": "N"
        }
        return tmap_dictionary.get(bids, None)
    except Exception as e: 
        logger.error(f"Error in tmap_no_bids_to_fsbid: {e}\n")
        return None


def fsbid_classifications_to_tmap(cs):
    tmap_classifications = []
    try:
        if type(cs) is list:
            for x in cs:
                tmap_classifications.append(
                    # resolves disrepancy between string and number comparison
                    pydash.to_number(x.get('te_id', None))
                )
        else:
            tmap_classifications.append(
                # resolves disrepancy between string and number comparison
                pydash.to_number(cs.get('te_id', None))
            )
    except Exception as e:
        logger.error(f"Error in fsbid_classifications_to_tmap: {e}\n")
        return None
    return tmap_classifications


def fsbid_assignments_to_tmap(assignments):
    from talentmap_api.fsbid.services.common import get_post_overview_url, get_post_bidding_considerations_url, get_obc_id
    assignmentsCopy = []
    tmap_assignments = []
    try:
        if type(assignments) is type(dict()):
            assignmentsCopy.append(assignments)
        else:
            assignmentsCopy = assignments
    except Exception as e:
        logger.error(f"Error creating assignmentsCopy: {e}\n")
        return None
    
    if type(assignmentsCopy) is type([]):
        for x in assignmentsCopy:
            pos = x.get('position', {})
            loc = pos.get('location', {})
            try:
                tmap_assignments.append(
                    {
                        "id": x.get('asg_seq_num', None),
                        "asg_seq_num": x.get('asg_seq_num', None),
                        "position_id": x.get('pos_seq_num', None),
                        "start_date": ensure_date(x.get('asgd_eta_date', None)),
                        "end_date": ensure_date(x.get('asgd_etd_ted_date', None)),
                        "position": {
                            "grade": pos.get("pos_grade_code", None),
                            "skill": f"{pos.get('pos_skill_desc', None)} ({pos.get('pos_skill_code')})",
                            "skill_code": pos.get("pos_skill_code", None),
                            "bureau": f"({pos.get('pos_bureau_short_desc', None)}) {pos.get('pos_bureau_long_desc', None)}",
                            "bureau_code": pydash.get(pos, 'pos_bureau_short_desc'), # only comes through for available bidders
                            "organization": pos.get('pos_org_short_desc', None),
                            "position_number": pos.get('pos_num_text', None),
                            "position_id": x.get('pos_seq_num', None),
                            "title": pos.get("pos_title_desc", None),
                            "post": {
                                "code": loc.get("gvt_geoloc_cd", None),
                                "post_overview_url": get_post_overview_url(loc.get("gvt_geoloc_cd", None)),
                                "post_bidding_considerations_url": get_post_bidding_considerations_url(loc.get("gvt_geoloc_cd", None)),
                                "obc_id": get_obc_id(loc.get("gvt_geoloc_cd", None)),
                                "location": {
                                    "country": loc.get("country", None),
                                    "code": loc.get("gvt_geoloc_cd", None),
                                    "city": loc.get("city", None),
                                    "state": loc.get("state", None),
                                }
                            },
                            "language": pos.get("pos_position_lang_prof_desc", None)
                        },
                    }
                )
            except Exception as e:
                logger.error(f"Error creating object for tmap_assignments: {e}\n")
                return None
    return tmap_assignments


def fsbid_languages_to_tmap(languages):
    # if no languages present (languages: [])
    if languages is None:
        return []

    tmap_languages = []
    empty_score = '--'
    try:
        for x in languages:
            # if x is None or not a dict, skip
            if x is None or not isinstance(x, dict):
                if x is None:
                    logger.warning(f"Skipping None value in languages: {languages}\n")
                continue
            if not x.get('empl_language', None) or not str(x.get('empl_language', None)).strip():
                continue
            r = str(x.get('empl_high_reading', '')).strip()
            s = str(x.get('empl_high_speaking', '')).strip()
            tmap_languages.append({
                "code": str(x.get('empl_language_code')).strip() if x.get('empl_language_code') else x.get('empl_language_code') or None,
                "language": str(x.get('empl_language')).strip() if x.get('empl_language') else x.get('empl_language') or None,
                "test_date": ensure_date(x.get('empl_high_test_date', None)),
                "speaking_score": s or empty_score,
                "reading_score": r or empty_score,
                "custom_description": f"{str(x.get('empl_language_code', None)).strip()} {s or empty_score}/{r or empty_score}"
            })
    except Exception as e:
        logger.error(f"Error mapping language in fsbid_languages_to_tmap:\n {e}\n")
        return None

    return tmap_languages


def fsbid_language_only_to_tmap(languages):
    # if no languages present (languages: [])
    if not languages:
        return "None"
    
    tmap_language_only = []

    try:
        for x in languages:
            # checks for non-dict elements such as [numbers, strings, None, etc] or
            # if the "empl_language" key is not present, skip
            if not isinstance(x, dict) or "empl_language" not in x:
                logger.warning(f"Skipping invalid language: {x}\n")
                continue

            # checks if the value for empl_language key is not a string, skip
            if not isinstance(x.get('empl_language'), str):
                continue

            # get the value for empl_language key, if its not present, give back None
            # strip the value to remove any leading/trailing whitespace
            empl_language = str(x.get('empl_language', None)).strip()
            if not empl_language:
                continue
            
            tmap_language_only.append(empl_language.strip())

        return ", ".join(str(x) for x in tmap_language_only)
    except Exception as e:
        logger.error(f"Error mapping language in fsbid_language_only_to_tmap:\n {e}\n")
        return None


def get_available_bidders(jwt_token, isCDO, query, host=None):
    from talentmap_api.fsbid.services.common import send_get_request
    from talentmap_api.cdo.services.available_bidders import get_available_bidders_stats
    cdo = 'cdo' if isCDO else 'bureau'
    uri = f"availablebidders/{cdo}"

    try:
        response = send_get_request(
            uri,
            query,
            convert_available_bidder_query,
            jwt_token,
            fsbid_available_bidder_to_talentmap,
            False, # No count function
            f"/api/v1/clients/availablebidders/{cdo}",
            host,
            CLIENTS_ROOT,
        )
    except Exception as e:
        logger.error(f"Error getting response from GET call in get_available_bidders: {e}\n")
        return None
    
    try:
        stats = get_available_bidders_stats(response)
        return {
            **stats,
            "results": list({v['perdet_seq_number']:v for v in response.get('results')}.values()),
        }
    except Exception as e:
        logger.error(f"Error getting stats in get_available_bidders: {e}\n")
        return None

# Can update to reuse client mapping once client v2 is updated and released with all the new fields
def fsbid_available_bidder_to_talentmap(data):
    employee = data.get('employee', None)
    current_assignment = None
    assignments = None
    position = None
    location = {}

    if employee is not None:
        current_assignment = employee.get('currentAssignment', None)

    if employee.get('assignment', None) is not None:
        assignments = employee.get('assignment', None)
        # handle if array
        if type(assignments) is type([]) and list(assignments):
            current_assignment = list(assignments)[0]
        # handle if object
        if type(assignments) is type(dict()):
            current_assignment = assignments
            # remove current prefix
            if assignments.get('currentPosition', None) is not None:
                assignments['position'] = assignments['currentPosition']
                assignments['position']['location'] = assignments['currentPosition']['currentLocation']
                assignments = [].append(assignments)

    if current_assignment is not None:
        # handle if object
        if current_assignment.get('currentPosition', None) is not None:
            position = current_assignment.get('currentPosition', None)
        # handle if array
        if current_assignment.get('position', None) is not None:
            position = current_assignment.get('position', None)

    if position is not None:
        # handle if object
        if position.get('currentLocation', None) is not None:
            location = position.get('currentLocation', {})
        # handle if array
        if position.get('location', None) is not None:
            location = position.get('location', {})

    if current_assignment and current_assignment.get('currentPosition', None) is not None:
        # remove current prefix
        current_assignment['position'] = current_assignment['currentPosition']
        current_assignment['position']['location'] = current_assignment['position']['currentLocation']

    # first object in array, mapped
    try:
        current_assignment = fsbid_assignments_to_tmap(current_assignment)[0]
    except:
        current_assignment = {}

    initials = None
    try:
        initials = employee['per_first_name'][:1] + employee['per_last_name'][:1]
    except:
        initials = None

    middle_name = get_middle_name(employee)
    suffix_name = f" {employee['per_suffix_name']}" if pydash.get(employee, 'per_suffix_name') else ''

    try:
        res = {
            "id": str(employee.get("pert_external_id", None)),
            "cdo": {
                "full_name": data.get('cdo_fullname', None),
                "last_name": data.get('cdo_last_name', None),
                "first_name": data.get('cdo_first_name', None),
                "email": data.get('cdo_email', None),
                "hru_id": data.get("hru_id", None),
            },
            "name": f"{employee.get('per_last_name', None)}{suffix_name}, {employee.get('per_first_name', None)} {middle_name['initial']}",
            "shortened_name": f"{employee.get('per_first_name', None)} {middle_name['initial']}{employee.get('per_last_name', None)}{suffix_name}",
            "initials": initials,
            "perdet_seq_number": str(employee.get("perdet_seq_num", None)),
            "grade": employee.get("per_grade_code", None),
            "skills": map_skill_codes(employee),
            "employee_id": str(employee.get("pert_external_id", None)),
            "role_code": data.get("rl_cd", None),
            "pos_location": map_location(location),
            # not exposed in FSBid yet
            # "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
            # "noPanel": fsbid_no_successful_panel_to_tmap(data.get("no_successful_panel")),
            # "noBids": fsbid_no_bids_to_tmap(data.get("no_bids")),
            "classifications": fsbid_classifications_to_tmap(employee.get("classifications", [])),
            "current_assignment": current_assignment,
            "assignments": fsbid_assignments_to_tmap(assignments),
            "languages": fsbid_languages_to_tmap(data.get('languages', []) or []),
            "available_bidder_details": {
                **data.get("details", {}),
                "is_shared": pydash.get(data, 'details.is_shared') == '1',
                "archived": pydash.get(data, 'details.archived') == '1',
            }
        }
        return res
    except Exception as e:
        logger.error(f"Error creating res object in fsbid_available_bidder_to_talentmap: {e}\n")
        return None


def convert_available_bidder_query(query):
    try:
        sort_asc = query.get("ordering", "name")[0] != "-"
        ordering = query.get("ordering", "name").lstrip("-")
        values = {
            "order_by": ordering,
            "is_asc": 'true' if sort_asc else 'false',
            "ad_id": query.get("ad_id", None),
        }

        return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
    except Exception as e:
        logger.error(f"Error in convert_available_bidder_query: {e}\n")
        return None
