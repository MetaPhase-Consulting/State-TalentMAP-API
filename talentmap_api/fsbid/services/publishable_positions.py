import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
import csv
from copy import deepcopy
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import combine_pp_grade

PUBLISHABLE_POSITIONS_ROOT = settings.PUBLISHABLE_POSITIONS_API_URL

logger = logging.getLogger(__name__)


def get_capsule_description(id, jwt_token):
    '''
    Gets an individual capsule description
    '''
    capsule_description = services.send_get_request(
        "capsule",
        {"id": id},
        convert_capsule_query,
        jwt_token,
        fsbid_capsule_to_talentmap_capsule,
        None,
        "/api/v1/fsbid/publishablePositions/",
        None,
        PUBLISHABLE_POSITIONS_ROOT
    )
    return pydash.get(capsule_description, 'results[0]') or None

def update_capsule_description(jwt_token, id, description, last_updated_date, updater_id):
    '''
    Updates capsule description on publishable position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"{PUBLISHABLE_POSITIONS_ROOT}/capsule"
    url = f"{uri}?pos_seq_num={id}&capsule_descr_txt={description}&update_id={last_updated_date}&update_id={updater_id}&ad_id={ad_id}"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response

def fsbid_capsule_to_talentmap_capsule(capsule):
    '''
    Formats FSBid response to Talentmap format
    '''
    return {
        "id": capsule.get("pos_seq_num", None),
        "description": capsule.get("capsule_descr_txt", None),
        "last_updated_date": capsule.get("update_date", None),
        "updater_id": capsule.get("update_id", None),
    }

def convert_capsule_query(query):
    '''
    Converts TalentMap query to FSBid
    '''
    values = {
        "pos_seq_num": query.get("id", None),
        "ad_id": query.get("ad_id", None),
        "update_date": query.get("last_updated_date", None),
        "update_id": query.get("updater_id", None),
        "capsule_descr_txt": query.get("description", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)


def get_publishable_positions(query, jwt_token):
    '''
    Gets Publishable Positions
    '''
    args = {
        "proc_name": 'qry_modPublishPos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": publishable_positions_req_mapping,
        "response_mapping_function": publishable_positions_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def publishable_positions_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'I_SVT_CODE': '',
        'I_PPL_CODE': '',
        'I_GRD_CD': request.get('grades') or '',
        'I_SKL_CODE_POS': request.get('skills') or '',
        'I_SKL_CODE_STFG_PTRN': '',
        'I_ORG_CODE': request.get('orgs') or '',
        'I_POS_NUM_TXT': request.get('posNum') or '',
        'I_POS_OVRSES_IND': '',
        'I_PS_CD': '',
        'I_LLT_CD': '',
        'I_LANG_CD': '',
        'I_LR_CD': '',
        'I_BUREAU_CD': request.get('bureaus') or '',
        'I_PUBS_CD': request.get('statuses') or '',
        'I_JC_ID': '',
        'I_ORDER_BY': '',
    }

def publishable_positions_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Publishable Positions failed.")
        return None

    def pub_pos_map(x):
        return {
            'positionNumber': x.get('POS_NUM_TXT'),
            'skill': services.format_desc_code(x.get('SKL_DESC_POS'), x.get('SKL_CODE_POS')),
            'positionTitle': x.get('POS_TITLE_TXT'),
            'bureau': x.get('BUR_SHORT_DESC'),
            'org': services.format_desc_code(x.get('ORGS_SHORT_DESC'), x.get('ORG_CODE')),
            'status': x.get('PUBS_CD'),
            'language': x.get('LANG_DESCR_TXT'),
            'payPlan': x.get('PPL_CODE'),
            'grade': x.get('GRD_CD'),
            'combined_pp_grade': combine_pp_grade(x.get('PPL_CODE'), x.get('GRD_CD')),
            'positionDetails': x.get('PPOS_CAPSULE_DESCR_TXT'),
            'positionDetailsLastUpdated': x.get('PPOS_CAPSULE_MODIFY_DT'),
            'lastUpdated': x.get('PPOS_LAST_UPDT_TMSMP_DT'),
            'lastUpdatedUserID': x.get('PPOS_LAST_UPDT_USER_ID'),
            # FE not currently using the ones below
            'posSeqNum': x.get('POS_SEQ_NUM'),
            'aptSeqNum': x.get('APT_SEQUENCE_NUM'),
            'aptDesc': x.get('APT_DESCRIPTION_TXT'),
            'psCD': x.get('PS_CD'),
            'posLtext': x.get('POSLTEXT'),
            'lrDesc': x.get('LR_DESCR_TXT'),
            'posAuditExclusionInd': x.get('PPOS_AUDIT_EXCLUSION_IND'),
        }

    return list(map(pub_pos_map, data.get('QRY_MODPUBLISHPOS_REF')))


def edit_publishable_position(data, jwt_token):
    '''
    Edit Publishable Position
    '''
    args = {
        "proc_name": 'act_modCapsulePos',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": edit_publishable_position_req_mapping,
        "response_mapping_function": edit_publishable_position_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_publishable_position_req_mapping(request):
    return {
      'PV_API_VERSION_I': '',
      'PV_AD_ID_I': '',
      'I_POS_SEQ_NUM': request.get('posSeqNum') or '',
      'I_PPOS_CAPSULE_DESCR_TXT': request.get('positionDetails') or '',
      'I_PPOS_LAST_UPDT_USER_ID': request.get('lastUpdatedUserID') or '',
      'I_PPOS_LAST_UPDT_TMSMP_DT': request.get('lastUpdated') or '',
    }

def edit_publishable_position_res_mapping(data):
    if data.get('O_RETURN_CODE', -1) != 0:
        logger.error(f"Publishable Positions Edit error return code.")
        raise ValidationError('Publishable Positions Edit error return code.')


def get_publishable_positions_filters(jwt_token):
    '''
    Gets Filters for Publishable Positions Page
    '''
    args = {
        'proc_name': 'qry_lstfsbidSearch',
        'package_name': 'PKG_WEBAPI_WRAP',
        'request_body': {},
        'request_mapping_function': publishable_positions_filter_req_mapping,
        'response_mapping_function': publishable_positions_filter_res_mapping,
        'jwt_token': jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def publishable_positions_filter_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def publishable_positions_filter_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Publishable Positions filters failed.")
        return None

    def status_map(x):
        return {
            'code': x.get('PUBS_CD'),
            'description': x.get('PUBS_DESCR_TXT'),
        }
    def cycle_map(x):
        return {
            'code': x.get('CYCLE_ID'),
            'description': x.get('CYCLE_NM_TXT'),
        }
    def bureau_map(x):
        return {
            'description': x.get('ORGS_SHORT_DESC'),
        }
    def org_map(x):
        return {
            'code': x.get('ORG_CODE'),
            'description': f"{x.get('ORGS_SHORT_DESC')} ({x.get('ORG_CODE')})",
        }
    def skills_map(x):
        return {
            'code': x.get('SKL_CODE'),
            'description': x.get('SKL_DESC'),
        }
    def grade_map(x):
        return {
            'code': x.get('GRD_CD'),
            'description': x.get('GRD_DESCR_TXT'),
        }

    return {
        'statusFilters': list(map(status_map, data.get('QRY_LSTPUBSTATUS_DD_REF'))),
        'cycleFilters': list(map(cycle_map, data.get('QRY_LSTASSIGNCYCLE_DD_REF'))),
        'bureauFilters': list(map(bureau_map, data.get('QRY_LSTBUREAUS_DD_REF'))),
        'orgFilters': list(map(org_map, data.get('QRY_LSTORGSHORT_DD_REF'))),
        'skillsFilters': list(map(skills_map, data.get('QRY_LSTSKILLCODES_DD_REF'))),
        'gradeFilters': list(map(grade_map, data.get('QRY_LSTGRADES_DD_REF'))),
    }

def get_publishable_positions_csv(query, jwt_token, rl_cd, host=None):
    data = get_publishable_positions(query, jwt_token)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=publishable_positions_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Position Number"),
        smart_str(u"Skill"),
        smart_str(u"Position Title"),
        smart_str(u"Bureau"),
        smart_str(u"Organization"),
        smart_str(u"Pay Plan/Grade"),
        smart_str(u"Publishable Status"),
        smart_str(u"Language"),
        # smart_str(u"Bid Cycle"),
        # smart_str(u"TED"),
        # smart_str(u"Incumbent"),
        # smart_str(u"Default TOD"),
        # smart_str(u"Assignee"),
        # smart_str(u"Post Differential | Danger Pay"),
        # smart_str(u"Employee ID"),
        # smart_str(u"Employee Status"),
        smart_str(u"Position Details"),
    ])
    for x in data:
        writer.writerow([
            smart_str(x.get('positionNumber')),
            smart_str(x.get('skill').strip('()')),
            smart_str(x.get('positionTitle')),
            smart_str(x.get('bureau')),
            smart_str(x.get('org')),
            smart_str(combine_pp_grade(x.get('payPlan'), x.get('grade'))),
            smart_str(x.get('status')),
            smart_str(x.get('language')),
            # smart_str(x.get('bidCycle')), # We are not receiving this data yet from here -
            # smart_str(x.get('ted')),
            # smart_str(x.get('incumbent')),
            # smart_str(x.get('tod')),
            # smart_str(x.get('assignee')),
            # smart_str(x.get('post')),
            # smart_str(x.get('empID')),
            # smart_str(x.get('empStatus')), # - To here
            smart_str(x.get('positionDetails')),
        ])

    return response
