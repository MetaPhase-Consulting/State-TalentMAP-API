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
PUBLISHABLE_POSITIONS_V2_ROOT = settings.PUBLISHABLE_POSITIONS_API_V2_URL

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
        "uri": "",
        "query": query,
        "query_mapping_function": convert_ppos_query,
        "jwt_token": jwt_token,
        "mapping_function": publishable_positions_res_mapping,
        "count_function": get_ppos_count,
        "base_url": "/api/v2/publishablepositions/",
        "api_root": PUBLISHABLE_POSITIONS_V2_ROOT,
    }

    publishable_positions = services.send_get_request(
        **args
    )
    return publishable_positions or None

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
    fsbid_lang_data = {
        "poslanguage1code": data.get('poslanguage1code'),
        "poslanguage1desc": data.get('poslanguage1desc'),
        "poslanguage2code": data.get('poslanguage2code'),
        "poslanguage2desc": data.get('poslanguage2desc'),
        "posspeakproficiency1code": data.get('posspeakproficiency1code'),
        "posreadproficiency1code": data.get('posreadproficiency1code'),
        "posspeakproficiency2code": data.get('posspeakproficiency2code'),
        "posreadproficiency2code": data.get('posreadproficiency2code'),
    }

    return {
        'positionNumber': data.get('posnumtext'),
        'skill': services.format_desc_code(data.get('posskilldesc'), data.get('posskillcode')),
        'positionTitle': data.get('postitledesc'),
        'bureau': data.get('posbureaushortdesc'),
        'org': services.format_desc_code(data.get('posorgshortdesc'), data.get('posorgcode')),
        'status': data.get('posstatuscode'),
        'languages': services.parseLanguagesToArr(fsbid_lang_data),
        'payPlan': data.get('pospayplancode'),
        'grade': data.get('posgradecode'),
        'combined_pp_grade': combine_pp_grade(data.get('pospayplancode'), data.get('posgradecode')),
        'positionDetails': data.get('pposcapsuledescrtxt'),
        'positionDetailsLastUpdated': data.get('pposcapsulemodifydt'),
        'lastUpdated': data.get('pposlastupdttmsmpdt'),
        'lastUpdatedUserID': data.get('pposlastupdtuserid'),
        'psCD': data.get('ppospubscd'),
        # FE not currently using the ones below
        'posSeqNum': data.get('posseqnum'),
        'aptSeqNum': data.get('pposaptsequencenum'),
        'posAuditExclusionInd': data.get('pposauditexclusionind'),
    }

def convert_ppos_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 10)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'posbureaushortdesc', 'val': query.get("bureaus", None)},
            {'col': 'posgradecode', 'val': query.get("grades", None)},
            {'col': 'ppospubscd', 'val': query.get("statuses", None)},
            {'col': 'posorgcode', 'val': query.get("orgs", None)},
            {'col': 'posskillcode', 'val': query.get("skills", None)},
        ]),
    }
    if query.get("getCount") == 'true':
        values["rp.pageNum"] = 0
        values["rp.pageRows"] = 0
        values["rp.columns"] = "ROWCOUNT"

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def get_ppos_count(query, jwt_token, host=None, use_post=False):
    '''
    Get total number of panel meetings for panel meeting search
    '''

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_ppos_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "is_template": True,
        "api_root": PUBLISHABLE_POSITIONS_V2_ROOT,
    }
    return services.send_count_request(**args)

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
