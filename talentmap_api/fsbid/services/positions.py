import json
import logging
from urllib.parse import urlencode, quote

import pydash
from django.conf import settings

from talentmap_api.fsbid.services import common as services

POSITIONS_V2_ROOT = settings.POSITIONS_API_V2_URL
POSITIONS_ROOT = settings.POSITIONS_API_URL

logger = logging.getLogger(__name__)
RESULTS_CAP = settings.MANAGE_EL_RESULTS_LIMIT


def get_position(id, jwt_token):
    '''
    Gets an individual unavailable position by id
    '''
    position = services.send_get_request(
        "Positions",
        {"id": id},
        convert_pos_query,
        jwt_token,
        fsbid_pos_to_talentmap_pos,
        None,
        "/api/v1/fsbid/positions/",
    )

    return pydash.get(position, 'results[0]') or None

def get_positions(query, jwt_token):
    '''
    Gets generic positions
    '''
    positions = services.send_get_request(
        "",
        query,
        convert_position_query,
        jwt_token,
        fsbid_to_talentmap_pos,
        None,
        "/api/v2/positions/",
        None,
        POSITIONS_V2_ROOT,
    )

    return pydash.get(positions, 'results[0]') or {} 

def fsbid_pos_to_talentmap_pos(pos):
    '''
    Converts the response generic position from FSBid to a format more in line with the Talentmap position
    '''
    empty_score = '--'
    r1 = pos.get("pos_read_proficiency_1_code", None) or empty_score
    s1 = pos.get("pos_speak_proficiency_1_code", None) or empty_score
    l1 = pos.get("pos_language_1_desc", None)
    rep1 = f"{l1} {r1}/{s1}"
    r2 = pos.get("pos_read_proficiency_2_code", None) or empty_score
    s2 = pos.get("pos_speak_proficiency_2_code", None) or empty_score
    l2 = pos.get("pos_language_2_desc", None)
    rep2 = f"{l2} {r2}/{s2}"

    return {
        "id": pos.get("pos_seq_num", None),
        "status": None,
        "status_code": None,
        "ted": None,
        "posted_date": None,
        "availability": {
            "availability": None,
            "reason": None
        },
        "tandem_nbr": None,  # Only appears in tandem searches
        "position": {
            "id": pos.get("pos_seq_num", None),
            "grade": pos.get("pos_grade_code", None),
            "skill": f"{pos.get('pos_skill_desc', '')} {pos.get('pos_skill_code')}",
            "skill_code": pos.get("pos_skill_code", None),
            "skill_secondary": None,
            "skill_secondary_code": None,
            "bureau": f"({pos.get('pos_bureau_short_desc', None)}) {pos.get('pos_bureau_long_desc', None)}",
            "bureau_code": pos.get('pos_bureau_code', None),
            "organization": f"({pos.get('pos_org_short_desc', None)}) {pos.get('pos_org_long_desc', None)}",
            "organization_code": pos.get('pos_org_code', None),
            "pay_plan": pos.get('pos_pay_plan_code', None),
            "pay_plan_desc": pos.get('pos_pay_plan_desc', None),
            "tour_of_duty": None,
            "classifications": None,
            "representation": None,
            "availability": {
                "availability": None,
                "reason": None
            },
            "position_number": pos.get("pos_num_text", None),
            "title": pos.get("pos_title_desc", None),
            "is_overseas": None,
            "is_highlighted": None,
            "create_date": pos.get("pos_create_date", None),
            "update_date": pos.get("pos_update_date", None),
            "effective_date": pos.get("pos_effective_date", None),
            "posted_date": None,
            "description": {
                "id": None,
                "last_editing_user": None,
                "is_editable_by_user": None,
                "date_created": None,
                "date_updated": None,
                "content": None,
                "point_of_contact": None,
                "website": None
            },
            "current_assignment": {
                "user": None,
                "tour_of_duty": None,
                "status": None,
                "start_date": None,
                "estimated_end_date": None,
            },
            "commuterPost": {
                "description": None,
                "frequency": None,
            },
            "post": {
                "id": None,
                "code": pos.get("pos_location_code", None),
                "tour_of_duty": None,
                "post_overview_url": None,
                "post_bidding_considerations_url": None,
                "cost_of_living_adjustment": None,
                "differential_rate": pos.get("bt_differential_rate_num", 0),
                "danger_pay": pos.get("bt_danger_pay_num", 0),
                "rest_relaxation_point": None,
                "has_consumable_allowance": None,
                "has_service_needs_differential": None,
                "obc_id": services.get_obc_id(pos.get("pos_location_code", None)),
                "location": {
                    "country": pos.get("location_country", None),
                    "code": pos.get("pos_location_code", None),
                    "city": pos.get("location_city", None),
                    "state": pos.get("location_state", None),
                },
            },
            "latest_bidcycle": {
                "id": None,
                "name": None,
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": None,
            },
            "languages": [
                {
                    "language": l1,
                    "reading_proficiency": r1,
                    "spoken_proficiency": s1,
                    # Fix this
                    "representation": rep1,
                },
                {
                    "language": l2,
                    "reading_proficiency": r2,
                    "spoken_proficiency": s2,
                    # Fix this
                    "representation": rep2,
                },
            ],
        },
        "bidcycle": {
            "id": None,
            "name": None,
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": None,
        },
        "bid_statistics": [{
            "id": None,
            "total_bids": None,
            "in_grade": None,
            "at_skill": None,
            "in_grade_at_skill": None,
            "has_handshake_offered": None,
            "has_handshake_accepted": None
        }],
        "unaccompaniedStatus": None,
        "isConsumable": None,
        "isServiceNeedDifferential": None,
        "isDifficultToStaff": None,
        "isEFMInside": None,
        "isEFMOutside": None,
    }


def convert_pos_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''

    values = {
        "request_params.pos_seq_num": query.get("id", None),
        "request_params.ad_id": query.get("ad_id", None),
        "request_params.page_index": query.get("page", 1),
        "request_params.page_size": query.get("limit", None),
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.pos_num_text": query.get("position_num", None),
    }

    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def convert_position_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 15)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'posnumtext', 'val': query.get("position_num", None)}
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_to_talentmap_pos(data):
    data['languages'] = services.parseLanguagesToArr(data)

    return {
        'pos_seq_num': data.get('posseqnum'),
        # Clean up redundant naming
        'organization': data.get('posorgshortdesc'),
        'pos_org_short_desc': data.get('posorgshortdesc'),
        'pos_org_code': data.get('posorgcode'),
        'pos_org_long_desc': data.get('posorglongdesc'),
        # Clean up redundant naming
        'position_number': data.get('posnumtext'),
        'pos_num_text': data.get('posnumtext'),
        # Clean up redundant naming
        'grade': data.get('posgradecode'),
        'pos_grade_code': data.get('posgradecode'),
        'pos_grade_desc': data.get('posgradedesc'),
        # Clean up redundant naming
        'title': data.get('postitledesc'),
        'pos_title_desc': data.get('postitledesc'),
        'pos_title_code': data.get('postitlecode'),
        'languages': data.get('languages'),
        'pos_update_id': data.get('posupdateid'),
        'pos_update_date': data.get('posupdatedate'),
        'pos_create_id': data.get('poscreateid'),
        'pos_create_date': data.get('poscreatedate'),
        'pos_effective_date': data.get('poseffectivedate'),
        'pos_job_code': data.get('posjobcodecode'),
        'pos_job_category_desc': data.get('posjobcategorydesc'),
        'pos_bureau_code': data.get('posbureaucode'),
        'pos_bureau_short_desc': data.get('posbureaushortdesc'),
        'pos_bureau_long_desc': data.get('posbureaulongdesc'),
        'pos_skill_code': data.get('posskillcode'),
        'pos_skill_desc': data.get('posskilldesc'),
        'pos_staff_pattern_skill_code': data.get('posstaffptrnskillcode'),
        'pos_staff_pattern_skill_desc': data.get('posstaffptrnskilldesc'),
        'pos_overseas_ind': data.get('posoverseasind'),
        # Clean up redundant naming
        'pay_plan': data.get('pospayplancode'),
        'pos_pay_plan_code': data.get('pospayplancode'),
        'pos_pay_plan_desc': data.get('pospayplandesc'),
        'pos_status_code': data.get('posstatuscode'),
        'pos_status_desc': data.get('posstatusdesc'),
        'pos_post_code': data.get('pospostcode'),
        'pos_location_code': data.get('poslocationcode'),
        'bt_dsc_cd': data.get('btdsccd'),
        'bt_us_code': data.get('btuscode'),
        'bt_bts_code': data.get('btbtscode'),
        'bt_sp_code': data.get('btspcode'),
        'bt_qt_code': data.get('btqtcode'),
        'bt_ht_code': data.get('bthtcode'),
        'bt_tod_code': data.get('bttodcode'),
        'bt_ehcp_code': data.get('btehcpcode'),
        'todo_pos_seq_num': data.get('todoposseqnum'),
        'todo_tod_code': data.get('todo_tod_code'),
    }


def get_frequent_positions(query, jwt_token):
    '''
    Get all frequent positions
    '''
    args = {
        "uri": "classifications",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_frequent_positions,
        "count_function": None,
        "base_url": "/api/v1/positions/",
        "api_root": POSITIONS_ROOT,
    }

    frequentPositions = services.send_get_request(
        **args
    )

    return frequentPositions

def fsbid_to_talentmap_frequent_positions(data):
    data = pydash.get(data, 'position') or []
    position = data[0] if data else {}

    return {
        'pos_seq_num': position.get('posseqnum'),
        'pos_org_short_desc': position.get('posorgshortdesc'),
        'pos_num_text': position.get('posnumtext'),
        'pos_grade_code': position.get('posgradecode'),
        'pos_title_desc': position.get('postitledesc'),
        'pay_plan': position.get('pospayplancode'),
    }


def get_el_positions(query, jwt_token):
    '''
    Gets Entry Level Positions
    '''
    args = {
        "proc_name": "prc_lst_tracking_details_grid",
        "package_name": "PKG_WEBAPI_WRAP",
        "request_body": query,
        "request_mapping_function": el_postions_req_mapping,
        "response_mapping_function": el_postions_res_mapping,
        "jwt_token": jwt_token,
    }

    return services.send_post_back_office(
        **args
    )

def el_postions_req_mapping(request):
    result = {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }
    for key in request:
        values_formatted = []
        if key == 'page':
            result['PV_PAGE_I'] = request[key]
        elif key == 'limit':
            result['PV_PAGE_ROWS_I'] = request[key]
        elif key == 'el-tps':
            for tp in request[key].split(','):
                values_formatted.append(f"{{\"TP_CODE\": \"{tp}\"}}")
            result['PTYP_TP_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-bureaus':
            for bur in request[key].split(','):
                values_formatted.append(f"{{\"BUREAU_ORG_CODE\": \"{bur}\"}}")
            result['PTYP_BUREAU_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-orgs':
            for org in request[key].split(','):
                values_formatted.append(f"{{\"ORG_SHORT_DESC\": \"{org}\"}}")
            result['PTYP_ORG_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-grades':
            for grade in request[key].split(','):
                values_formatted.append(f"{{\"GRD_GRADE_CODE\": \"{grade}\"}}")
            result['PTYP_GRADE_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-skills':
            for skl in request[key].split(','):
                values_formatted.append(f"{{\"SKL_CODE\": \"{skl}\"}}")
            result['PTYP_SKILL_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-jobs':
            for jc in request[key].split(','):
                values_formatted.append(f"{{\"JC_ID\": \"{jc}\"}}")
            result['PTYP_JC_DD_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-language':
            for lang in request[key].split(','):
                values_formatted.append(f"{{\"LANG_CODE\": \"{lang}\"}}")
            result['PTYP_LANGUAGE_TAB_I'] = f"{{\"Data\": [{','.join(values_formatted)}]}}"
        elif key == 'el-overseas':
            result['PTYP_OVERSEAS_TAB_I'] = f"{{\"Data\": {{\"POS_OVERSEAS_IND\": \"O\"}}}}"
        elif key == 'el-domestic':
            result['PTYP_OVERSEAS_TAB_I'] = f"{{\"Data\": {{\"POS_OVERSEAS_IND\": \"D\"}}}}"
        elif key == 'text':
            result['PV_FREETEXT_I'] = request[key]
        
    return result

def el_postions_res_mapping(data):
    if data is None or (data['PV_RETURN_CODE_O'] and data['PV_RETURN_CODE_O'] is not 0):
        logger.error(f"Fsbid call for Entry Level filters failed.")
        return None

    def el_pos_map(x):
        return {
            'POS_SEQ_NUM': x.get('POS_SEQ_NUM'),
            'positionNumber': x.get('POS_NUM_TEXT'),
            'skill': x.get('POS_SKILL_CODE'),
            'positionTitle': x.get('POS_TITLE_DESC'),
            'bureau': x.get('BUREAU_SHORT_DESC'),
            'org': x.get('ORG_SHORT_DESC'),
            'grade': x.get('POS_GRADE_CODE'),
            'jobCategory': x.get('POS_JOB_CATEGORY'),
            'languages': x.get('POS_POSITION_LANG_PROF_CODE'),
            'OD': x.get('POS_OVERSEAS_DESC'),
            'incumbent': x.get('INCUMBENT'),
            'incumbentTED': x.get('INCUMBENT_TED'),
            'assignee': x.get('ASSIGNEE'),
            'assigneeTED': x.get('ASSIGNEE_TED'),
            'ELTOML': x.get('ELTOML'),
            'EL': x.get('EL'),
            'MC': x.get('MC'),
            'LNA': x.get('LNA'),
            'FICA': x.get('FICA'),
            'mcEndDate': x.get('MC_END_DATE'),
        }

    final = {
        "count": data.get('PV_ROWCOUNT_O') or 0,
        "results": list(map(el_pos_map, data.get('PQRY_TRACKING_DETAIL_O')[:int(RESULTS_CAP)])),
    }

    return final

def get_el_positions_filters(request, jwt_token):
    '''
    Gets Filters for Manage EL Page
    '''
    args = {
        'proc_name': 'prc_tracking_detail_pos_search',
        'package_name': 'PKG_WEBAPI_WRAP',
        'request_body': {},
        'request_mapping_function': el_positions_filter_req_mapping,
        'response_mapping_function': el_positions_filter_res_mapping,
        'jwt_token': jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def el_positions_filter_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def el_positions_filter_res_mapping(data):
    if data is None or (data['PV_RETURN_CODE_O'] and data['PV_RETURN_CODE_O'] is not 0):
        logger.error(f"Fsbid call for Entry Level filters failed.")
        return None

    def TP_map(x):
        return {
            'code': x.get('TP_CODE'),
            'description': x.get('TP_DESCR_TXT'),
        }
    def bureau_map(x):
        return {
            'code': x.get('BUREAU_ORG_CODE'),
            'short_description': x.get('BUREAU_SHORT_DESC'),
            'description': x.get('BUREAU_LONG_DESC'),
        }
    def org_map(x):
        # WS payload does not include ORG_CODE, only ORG_SHORT_DESC
        return {
            'code': x.get('ORG_SHORT_DESC'),
            'description': x.get('ORG_SHORT_DESC'),
        }
    def grade_map(x):
        return {
            'code': x.get('GRD_GRADE_CODE'),
            'description': x.get('GRD_GRADE_CODE'),
        }
    def skills_map(x):
        return {
            'code': x.get('SKL_CODE'),
            'description': x.get('SKL_DESC'),
            'custom_description': f"{x.get('SKL_CODE')} {x.get('SKL_DESC')}",
        }
    def jc_map(x):
        return {
            'code': x.get('JC_ID'),
            'description': x.get('JC_NM_TXT'),
        }
    def languages_map(x):
        return {
            'code': x.get('LANG_CODE'),
            'description': x.get('LANG_LONG_DESC'),
        }


    return {
        'tpFilters': list(map(TP_map, data.get('PTYP_TP_TAB_O'))),
        'bureauFilters': list(map(bureau_map, data.get('PTYP_BUREAU_TAB_O'))),
        'orgFilters': list(map(org_map, data.get('PTYP_ORG_TAB_O'))),
        'gradeFilters': list(map(grade_map, data.get('PTYP_GRADE_TAB_O'))),
        'skillsFilters': list(map(skills_map, data.get('PTYP_SKILL_TAB_O'))),
        'jcFilters': list(map(jc_map, data.get('PTYP_JC_TAB_O'))),
        'languageFilters': list(map(languages_map, data.get('PTYP_LANGUAGE_TAB_O'))),
    }

def edit_el_positions(data, jwt_token):
    '''
    Edit and save an Entry Level Position. Utilize common functionality send_post_back_office(...) 
    in commons.py to make an edit POST to Web Services BackOfficeCRUD
    '''


    '''
    So we are turning two things into a JSON string - the value of Data which contains the 
    things we will be changing for a specific EL position, and then the whole jsonInput (which CONTAINS the 
    aforementioned Data) which is the whole payload that will be sent to the Web Service.
    '''

    # Web Service JSON Input for EL Position edit
    # payload = {
    #             "PV_API_VERSION_I": "",
    #             "PV_AD_ID_I": "",
    #             "PV_ACTION_I": "",
    #             "PTYP_CUST_TD_POS_TAB_I": {"Data": data}
    #             }

    payload = {
        'PV_API_VERSION_I': '', 
        'PV_AD_ID_I': '', 
        'PV_ACTION_I': '', 
        'PTYP_CUST_TD_POS_TAB_I': f"'Data': {data}"
    }
    # 'PTYP_CUST_TD_POS_TAB_I': f"{{\"Data\": {json.dumps(data)}}}"

    # payload = {
    #     "PV_API_VERSION_I": "", 
    #     "PV_AD_ID_I": "", 
    #     "PV_ACTION_I": "", 
    #     "PTYP_CUST_TD_POS_TAB_I": {"Data": "[{'POS_SEQ_NUM': 11, 'EL': 'true', 'LNA': 'false', 'FICA': 'false', 'ELTOML': 'false', 'MC': 'false'}]"}
    #     }
    logger.info(f"Edit EL Position Payload: {payload}")
    # previous - "PTYP_CUST_TD_POS_TAB_I": {"Data": json.dumps(data)}

    # this will only be if what we are passed from the ActionView is just the 
    # VALUE of Data key. 2 version - 1st one will print out the string with 
    # the souble quotes surrounding it, the second will make all of it a string 
    # but not print out the double quotes
    # formatted_PTYP_CUST_TD_POS_TAB_I = f"\"{{\"Data\": {data}}}\""
    # formatted_PTYP_CUST_TD_POS_TAB_I = f"{{\"Data\": {data}}}"
    # logger.info(f"formatted_PTYP_CUST_TD_POS_TAB_I: {formatted_PTYP_CUST_TD_POS_TAB_I}\n")
    # logger.info(f"type of formatted_PTYP_CUST_TD_POS_TAB_I: {type(formatted_PTYP_CUST_TD_POS_TAB_I)}\n")

    # payload = {
    #                 "PV_API_VERSION_I": "",
    #                 "PV_AD_ID_I": "",
    #                 "PTYP_CUST_TD_POS_TAB_I": "{Data:[{'POS_SEQ_NUM':'11', 'ELTOML':'true'}]"
    #     }

    # payload = {
    #             "PV_API_VERSION_I": "",
    #             "PV_AD_ID_I": "",
    #             "PTYP_CUST_TD_POS_TAB_I": "{Data:[{'POS_SEQ_NUM':'11', 'MC':'false','MC_END_DATE':'07/28/2024'}]"
    #         }
    
    # convert payload to json string
    # json_input = json.dumps(payload)
    # json_input = payload
    # logger.info(f"Edit EL Position JSON Input: {json_input}")
    # logger.info(f"json_input type: {type(json_input)}")

    args = {
        "proc_name": "prc_iud_tracking_details_pos",
        "package_name": "PKG_WEBAPI_WRAP", # "PKG_WEBAPI_WRAP",
        "request_body": payload,
        "request_mapping_function": None,
        "response_mapping_function": None,
        "jwt_token": jwt_token,
    }

    try:
        response = services.send_post_back_office(**args)
        logger.info(f"Edit EL Position Response: {response}")
        return response
    except Exception as e:
        logger.info(f"An error occurred in edit_el_positions: {e}")
        return None
