import csv
import logging
from functools import partial
from urllib.parse import urlencode, quote
from datetime import datetime
import jwt
import pydash

from django.conf import settings
from django.http import QueryDict
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.fsbid.services import common as services
from talentmap_api.fsbid.services import client as client_services
import talentmap_api.fsbid.services.agenda_item_validator as ai_validator
from talentmap_api.common.common_helpers import ensure_date, sort_legs, combine_pp_grade
from talentmap_api.fsbid.requests import requests

AGENDA_API_ROOT = settings.AGENDA_API_URL
PANEL_API_ROOT = settings.PANEL_API_URL
CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL
API_ROOT = settings.WS_ROOT_API_URL

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

    ai_return = pydash.get(agenda_item, 'results[0]') or None

    if ai_return:
        # Get Vice/Vacancy data
        pos_seq_nums = []
        legs = pydash.get(ai_return, "legs")
        for leg in legs:
            if ('ail_pos_seq_num' in leg) and (leg["ail_pos_seq_num"] is not None):
                pos_seq_nums.append(leg["ail_pos_seq_num"])
        vice_lookup = get_vice_data(pos_seq_nums, jwt_token)

        # Add Vice/Vacancy data to AI for AIM page
        for leg in legs:
            if 'ail_pos_seq_num' in leg:
                if leg["is_separation"]:
                    leg["vice"] = {}
                else:
                    leg["vice"] = vice_lookup.get(leg["ail_pos_seq_num"]) or {}
    return ai_return


def get_agenda_items(jwt_token=None, query={}, host=None):
    '''
    Get agenda items
    '''
    from talentmap_api.fsbid.services.agenda_employees import get_agenda_employees
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "host": host,
        "use_post": False,
        "api_root": AGENDA_API_ROOT,
    }

    agenda_items = services.send_get_request(
        **args
    )

    # if perdet is none, don't get employee data
    perdet = query.get('perdet', None)
    if perdet is not None:
        employeeQuery = QueryDict(f"limit=1&page=1&perdet={query.get('perdet', None)}")
        employee = get_agenda_employees(employeeQuery, jwt_token, host)        
        return {
            "employee": employee,
            "results": agenda_items,
        }
    
    return agenda_items

def modify_agenda(query={}, jwt_token=None, host=None):
    '''
    Create/Edit Agenda
    '''
    ai_validation = ai_validator.validate_agenda_item(query)

    if not ai_validation['allValid']:
        return ai_validation

    # Possible ref data for comparison to determine create or edit
    refData = query.get("refData")

    # Inject decoded hru_id
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    query['hru_id'] = hru_id

    # Unpack PMI request
    pmi_mic_code = query.get("panelMeetingCategory")
    pmi_pm_seq_num = query.get("panelMeetingId")

    # Original PMI
    existing_pmi_seq_num = refData.get("pmi_seq_num")
    existing_pmi_mic_code = refData.get("pmi_mic_code")
    existing_pmi_pm_seq_num = refData.get("pmi_pm_seq_num")
    
    newly_created_pmi_seq_num = None

    try:
        if pmi_mic_code or pmi_pm_seq_num:
            if existing_pmi_seq_num:
                if (pmi_mic_code != existing_pmi_mic_code) or (pmi_pm_seq_num != existing_pmi_pm_seq_num):
                    panel_meeting_item = edit_panel_meeting_item(query, jwt_token)
            else:
                 panel_meeting_item = create_panel_meeting_item(query, jwt_token)
                 newly_created_pmi_seq_num = pydash.get(panel_meeting_item, '[0].pmi_seq_num')
    except Exception as e:
        logger.error("Error updating/creating PMI")
        logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return 

    # Only continue if PMI exists
    if newly_created_pmi_seq_num or existing_pmi_pm_seq_num:
        try:
            # Inject PMI seq num into query
            query['pmiseqnum'] = newly_created_pmi_seq_num if newly_created_pmi_seq_num else existing_pmi_pm_seq_num

            # Unpack AI request
            status_code = query.get("agendaStatusCode")
            tod_code = query.get("combinedTod")
            tod_combined_months_num = query.get("combinedTodMonthsNum")
            tod_combined_other_text = query.get("combinedTodOtherText")
            asg_seq_num = query.get("assignmentId")
            asg_revision_num = query.get("assignmentVersion")

            # Original AI
            existing_asg = refData.get("assignment", {})
            existing_ai_seq_num = refData.get("id")
            existing_status_code = refData.get("status_short")
            existing_tod_code = refData.get("aiCombinedTodCode")
            existing_tod_combined_months_num = refData.get("aiCombinedTodMonthsNum")
            existing_tod_combined_other_text = refData.get("aiCombinedTodOtherText")
            existing_asg_seq_num = existing_asg.get("id")
            existing_asg_revision_num = existing_asg.get("revision_num")

            newly_created_ai_seq_num = None

            if (status_code or tod_code or tod_combined_months_num or 
                tod_combined_other_text or asg_seq_num or asg_revision_num):
                if existing_ai_seq_num:
                    if ((status_code != existing_status_code) or
                        (tod_code != existing_tod_code) or
                        (tod_combined_months_num != existing_tod_combined_months_num) or
                        (tod_combined_other_text != existing_tod_combined_other_text) or
                        (asg_seq_num != existing_asg_seq_num) or
                        (asg_revision_num != existing_asg_revision_num)
                    ):
                        edit_agenda_item(query, jwt_token)
                else:
                    agenda_item = create_agenda_item(query, jwt_token)
                    newly_created_ai_seq_num = pydash.get(agenda_item, '[0].ai_seq_num')
        except Exception as e:
            logger.error("Error updating/creating AI")
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            return 

        try:
            # Only continue if AI exists
            if newly_created_ai_seq_num or existing_ai_seq_num:
                query["aiseqnum"] = newly_created_ai_seq_num if newly_created_ai_seq_num else existing_ai_seq_num
                
                # Unpack existing AIL
                existing_legs = refData.get("legs")

                # Unpack new AIL
                legs = query.get("agendaLegs")

                if legs:
                    if existing_legs:
                        # Delete existing AILs 
                        # Create new AILs from payload - assumes validator caught any errors beforehand
                        existing_ails = [{"ailseqnum": x.get("ail_seq_num"), "ailupdatedate": x.get("ail_update_date", "").replace("T", " "),} for x in existing_legs if x.get("ail_seq_num")]
                        for ail in existing_ails:
                            ai_seq_num = query["aiseqnum"]
                            delete_agenda_item_leg(ail, ai_seq_num, jwt_token)
                    for leg in legs:
                        agenda_item_leg = create_agenda_item_leg(leg, query, jwt_token)
                        if not pydash.get(agenda_item_leg, "[0].ail_seq_num"):
                            logger.error("Error creating AIL")
                
                # Unpack existing AIR/AIRI
                existing_remarks = refData.get("remarks")
                
                # Unpack new AIR/AIRI
                remarks = query.get("remarks")
                
                # Always delete regardless of query, for empty remarks edge case
                if existing_remarks:
                    for air in existing_remarks:
                        delete_agenda_item_remark(air, jwt_token)
                if remarks:
                    for remark in remarks:
                        remark_inserts = remark.get("user_remark_inserts")
                        agenda_item_remark = create_agenda_item_remark(remark, query, jwt_token)
                        if not pydash.get(agenda_item_remark, "[0].rmrk_seq_num"):
                            logger.error("Error creating AIR")
                        elif remark_inserts:
                            for insert in remark_inserts:
                                agenda_item_remark_insert = create_agenda_item_remark_insert(insert, query, jwt_token)
                                if not pydash.get(agenda_item_remark_insert, "[0].ri_seq_num"):
                                    logger.error("Error creating AIRI")
            else:
                logger.error("AI does not exist")
        except Exception as e:
            logger.error("Error updating/creating AIL")
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            return 

        return newly_created_ai_seq_num or existing_ai_seq_num
    else:
        logger.error("PMI does not exist")


   

def create_panel_meeting_item(query, jwt_token):
    '''
    Create PMI
    '''
    args = {
        "uri": "v1/panels/meetingItem",
        "query": query,
        "query_mapping_function": convert_create_panel_meeting_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )


def edit_panel_meeting_item(query, jwt_token):
    '''
    Edit PMI
    '''
    pmiseqnum = query.get("refData", {}).get("pmi_seq_num")
    args = {
        "uri": f"v1/panels/meetingItem/{pmiseqnum}",
        "query": query,
        "query_mapping_function": convert_edit_panel_meeting_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.send_put_request(
        **args
    )


def create_agenda_item(query, jwt_token):
    '''
    Create AI
    '''
    args = {
        "uri": "v1/agendas",
        "query": query,
        "query_mapping_function": convert_create_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.send_post_request(
        **args
    )


def edit_agenda_item(query, jwt_token):
    '''
    Edit AI
    '''
    aiseqnum = query.get("refData", {}).get("id")
    args = {
        "uri": f"v1/agendas/{aiseqnum}",
        "query": query,
        "query_mapping_function": convert_edit_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.send_put_request(
        **args
    )

def delete_agenda_item(query, jwt_token):
    '''
    Deletes agenda item
    '''
    ai_seq_num = query.get("aiseqnum")
    ai_update_date = query.get("aiupdatedate")
    url = f"{API_ROOT}/v1/agendas/{ai_seq_num}?aiupdatedate={ai_update_date}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})

def delete_agenda_item_leg(query, ai_seq_num, jwt_token):
    '''
    Delete AIL
    '''
    # Move to common function if delete pattern emerges
    ail_seq_num = query.get("ailseqnum")
    ail_update_date = query.get("ailupdatedate")
    url = f"{API_ROOT}/v1/agendas/{ai_seq_num}/legs/{ail_seq_num}?ailupdatedate={ail_update_date}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})


def delete_agenda_item_remark(query, jwt_token):
    '''
    Delete AIR
    '''
    # Move to common function if delete pattern emerges
    aiseqnum = query.get("air_ai_seq_num")
    airrmrkseqnum = query.get("air_rmrk_seq_num")
    airupdatedate = query.get("air_update_date").replace("T", " ")
    url = f"{API_ROOT}/v1/agendas/{aiseqnum}/remarks/{airrmrkseqnum}?airupdatedate={airupdatedate}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})

def create_agenda_item_leg(data, query, jwt_token):
    '''
    Create AIL
    '''
    aiseqnum = query["aiseqnum"]
    args = {
        "uri": f"v1/agendas/{aiseqnum}/legs",
        "query": query,
        "query_mapping_function": partial(convert_agenda_item_leg_query, leg=data),
        "jwt_token": jwt_token,
        "mapping_function": ""
    }

    return services.send_post_request(
        **args
    )


def create_agenda_item_remark(data, query, jwt_token):
    '''
    Create AIR
    '''
    aiseqnum = query.get("aiseqnum")
    args = {
        "uri": f"v1/agendas/{aiseqnum}/remarks",
        "query": query,
        "query_mapping_function": partial(convert_create_agenda_item_remark_query, remark=data),
        "jwt_token": jwt_token,
        "mapping_function": ""
    }

    return services.send_post_request(
        **args
    )

def create_agenda_item_remark_insert(data, query, jwt_token):
    '''
    Create AIRI
    '''
    aiseqnum = query.get("aiseqnum")
    airrmrkseqnum = data.get("airirmrkseqnum")
    args = {
        "uri": f"v1/agendas/{aiseqnum}/remarks/{airrmrkseqnum}/inserts",
        "query": query,
        "query_mapping_function": partial(convert_create_agenda_item_remark_insert_query, insert=data),
        "jwt_token": jwt_token,
        "mapping_function": ""
    }

    return services.send_post_request(
        **args
    )


def convert_create_agenda_item_remark_insert_query(query, insert={}):
    return {
        "airiaiseqnum": query.get("aiseqnum"),
        "airirmrkseqnum": insert.get("airirmrkseqnum"),
        "aiririseqnum": insert.get("aiririseqnum"),
        "airiinsertiontext": insert.get("airiinsertiontext"),
        "airicreateid": query.get("hru_id"),
        "airiupdateid": query.get("hru_id"),
    }



def convert_create_agenda_item_remark_query(query, remark={}):
    return {
        "airaiseqnum": query.get("aiseqnum"),
        "airrmrkseqnum": remark.get("seq_num"),
        "airremarktext": remark.get("text"),
        "aircompleteind": "Y",
        "aircreateid": query.get("hru_id"),
        "airupdateid": query.get("hru_id"),
    }


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
            {'col': 'aiseqnum', 'val': query.get("aiseqnum", None)},
            {'col': 'pmipmseqnum', 'val': query.get("pmipmseqnum", None), 'com': 'IN' },
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_single_agenda_item_to_talentmap_single_agenda_item(data, ref_skills={}):
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
    statusFull = pydash.get(data, "aisdesctext") or None
    reportCategory = {
        "code": pydash.get(data, "Panel[0].pmimiccode") or None,
        "desc_text": pydash.get(data, "Panel[0].micdesctext") or None,
    }

    # skill code lookup against ref_skills data
    skill_descriptions = []
    if (ref_skills):
        codes_to_lookup = []
        codes_to_lookup.append(pydash.get(data, "person[0].perdetskillcode"))
        codes_to_lookup.append(pydash.get(data, "person[0].perdetskill2code"))
        codes_to_lookup.append(pydash.get(data, "person[0].perdetskill3code"))
        for skill_code in codes_to_lookup:
            if skill_code is not None and ref_skills.get(skill_code):
                skill_descriptions.append(f'({skill_code}) {ref_skills[skill_code]}')
    
    languages = pydash.get(data, "person[0].languages") or None
    languages_return = []
    if languages:
        for lang in languages:
            languages_return.append(fsbid_lang_to_talentmap_lang(lang))
    
    cdo = pydash.get(data, "person[0].cdo[0].user[0]") or None
    if cdo:
        cdo = fsbid_cdo_to_talentmap_cdo(cdo)

    org = pydash.get(data, "person[0].org[0]") or None
    if org:
        org = fsbid_org_to_talentmap_org(org)

    updaters = pydash.get(data, "updaters") or None
    if updaters:
        updaters = fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(updaters[0])

    creators = pydash.get(data, "creators") or None
    if creators:
        creators = fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(creators[0])

    # aitodcode is the agenda item combined tod code
    tod_code = pydash.get(data, "aitodcode")
    tod_other_text = pydash.get(data, "aicombinedtodothertext")
    is_other_tod = True if (tod_code == 'X') and (tod_other_text) else False

    pp = pydash.get(data, "person[0].perdetpayplancode")
    grade = pydash.get(data, "person[0].perdetgradecode")
    combined_pp_grade = combine_pp_grade(pp, grade)

    panel = data.get("Panel")[0]

    remarks = pydash.get(data, "remarks") or []
    if not remarks:
        logger.info("Remarks is empty")
        logger.info(f"aiseqnum: {data.get('aiseqnum')}")
    logger.info(f"Remarks BEFORE parsing: {remarks}")
    return {
        "id": data.get("aiseqnum") or None,
        "aiCombinedTodCode": data.get("aitodcode") or "",
        "aiCombinedTodDescText": data.get("aitoddesctext") or None,
        "aiCombinedTodMonthsNum": data.get("aicombinedtodmonthsnum") if is_other_tod else "", # only custom/other TOD should have months and other_text
        "aiCombinedTodOtherText": data.get("aicombinedtodothertext") if is_other_tod else "", # only custom/other TOD should have months and other_text
        "ahtCode": data.get("ahtcode") or None,
        "ahtDescText": data.get("ahtdesctext") or None,
        "aihHoldNum": data.get("aihholdnum") or None,
        "aihHoldComment": data.get("aihholdcommenttext") or None,
        "remarks": services.parse_agenda_remarks(data.get("remarks") or []),
        "pmd_dttm": panel.get("pmd_dttm") or None,
        "pmt_code": panel.get("pmtcode") or None,
        "pmi_pm_seq_num": panel.get("pmipmseqnum"),
        "pmi_seq_num": panel.get("pmiseqnum"),
        "pmi_official_item_num": panel.get("pmiofficialitemnum") or None,
        "pmi_addendum_ind": panel.get("pmiaddendumind") or None,
        "pmi_label_text": panel.get("pmilabeltext") or None,
        "pmi_mic_code": panel.get("pmimiccode"),
        "pmi_create_id": panel.get("pmicreateid"),
        "pmi_create_date": panel.get("pmicreatedate"),
        "pmi_update_id": panel.get("pmiupdateid"),
        "pmi_update_date": panel.get("pmiupdatedate"),
        "status_code": data.get("aiaiscode") or None,
        "status_full": statusFull,
        "status_short": agendaStatusAbbrev.get(statusFull, None),
        "report_category": reportCategory,
        "perdet": data.get("aiperdetseqnum") or None,
        "assignment": assignment,
        "legs": legsToReturn,
        "update_date": data.get("update_date"),  # TODO - find this date
        "modifier_name": data.get("aiupdateid") or None,  # TODO - this is only the id
        "modifier_date": data.get("aiupdatedate") or None, 
        "creator_name": data.get("aiitemcreatorid") or None,  # TODO - this is only the id
        "creator_date": data.get("aicreatedate") or None,
        "creators": creators,
        "updaters": updaters,
        "skills": skill_descriptions,
        "cdo": cdo,
        "languages": languages_return,
        "pay_plan_code": pp,
        "grade": grade,
        "combined_pp_grade": combined_pp_grade,
        "full_name": services.remove_nmn(pydash.get(data, "person[0].perpiifullname")),
        "org": org,
    }


def fsbid_agenda_items_to_talentmap_agenda_items(data, jwt_token=None):
    ai_id = data.get("aiseqnum", None)

    agenda_item = get_single_agenda_item(jwt_token, ai_id)

    return {
        "id": data.get("aiseqnum", None),
        **agenda_item,
    }


def fsbid_legs_to_talentmap_legs(data):
    tod_code = pydash.get(data, "ailtodcode")
    tod_short_desc = pydash.get(data, "todshortdesc")
    tod_long_desc = pydash.get(data, "toddesctext")
    # only custom/other TOD will have other_text
    tod_other_text = pydash.get(data, "ailtodothertext")
    tod_months = pydash.get(data, "ailtodmonthsnum")
    is_other_tod = True if (tod_code == 'X') and (tod_other_text) else False
    tod_is_active = pydash.get(data, "todstatuscode") == "A"
    # legacy and custom/other TOD Agenda Item Legs will not render as a dropdown
    tod_is_dropdown = (tod_code != "X") and (tod_is_active is True)
    city = pydash.get(data, 'ailcitytext') or ''
    country_state = pydash.get(data, 'ailcountrystatetext') or ''
    code = pydash.get(data, 'aildsccd')
    location = f"{city}{', ' if (city and country_state) else ''}{country_state}" or code
    lat_code = pydash.get(data, 'aillatcode')
    skills_data = services.get_skills(pydash.get(data, 'agendaLegPosition[0]', {}))
    eta_date = data.get("ailetadate", None)
    ted_date = data.get("ailetdtedsepdate", None)
    pay_plan = pydash.get(data, "agendaLegPosition[0].pospayplancode")
    grade = pydash.get(data, "agendaLegPosition[0].posgradecode")
    combined_pp_grade = combine_pp_grade(pay_plan, grade)
    not_applicable = '-'

    res = {
        "id": pydash.get(data, "ailaiseqnum", None),
        "ail_seq_num": pydash.get(data, "ailseqnum", None),
        "ail_update_date": data.get("ailupdatedate"),
        "ail_pos_seq_num": pydash.get(data, "ailposseqnum", None),
        "ail_cp_id": pydash.get(data, "ailcpid", None),
        "ail_asg_seq_num": pydash.get(data, "ailasgseqnum", None),
        "ail_asgd_revision_num": pydash.get(data, "ailasgdrevisionnum", None),
        "pos_title": pydash.get(data, "agendaLegPosition[0].postitledesc", None),
        "pos_num": pydash.get(data, "agendaLegPosition[0].posnumtext", None),
        "org": pydash.get(data, "agendaLegPosition[0].posorgshortdesc", None),
        "eta": pydash.get(data, "ailetadate", None),
        "ted": not_applicable if tod_long_desc == 'INDEFINITE' else pydash.get(data, "ailetdtedsepdate", None),
        "tod": tod_code,
        "tod_is_dropdown": tod_is_dropdown,
        "tod_months": tod_months if is_other_tod else None, # only a custom/other TOD should have months
        "tod_short_desc": tod_other_text if is_other_tod else tod_short_desc,
        "tod_long_desc": tod_other_text if is_other_tod else tod_long_desc,
        "languages": services.parseLanguagesToArr(pydash.get(data, "agendaLegPosition[0]", None)),
        "action": pydash.get(data, "latabbrdesctext", None),
        "action_code": lat_code,
        "travel_code": data.get("ailtfcd"),
        "travel_desc": data.get("ailtfdescr") or None,
        "is_separation": False,
        "sort_date": eta_date or ted_date or None,  # AgendaItems sort legs by ETA, then by TED
        "pay_plan": pay_plan,
        "grade": grade,
        "combined_pp_grade": combined_pp_grade,
        "pay_plan_desc": pydash.get(data, "agendaLegPosition[0].pospayplandesc", None),
        "skill": skills_data.get("skill_1_representation"),
        "skill_code": skills_data.get("skill_1_code"),
        "skill_secondary": skills_data.get("skill_2_representation"),
        "skill_secondary_code": skills_data.get("skill_2_code"),
        "custom_skills_description": skills_data.get("combined_skills_representation"),
    }

    # Remove fields not applicable for separation leg action types
    separation_types = ['H', 'M', 'N', 'O', 'P']
    if lat_code in separation_types:
        res['is_separation'] = True
        res['sort_date'] = data.get("ailetdtedsepdate", None)  # Separations are sorted by TED
        res['pos_title'] = pydash.get(data, 'latdesctext')
        res['pos_num'] = not_applicable
        res['eta'] = not_applicable
        res['tod'] = not_applicable
        res['tod_short_desc'] = not_applicable
        res['tod_months'] = None
        res['tod_long_desc'] = not_applicable
        res['combined_pp_grade'] = not_applicable
        res['languages'] = not_applicable
        res['org'] = location
        res['custom_skills_description'] = not_applicable
        res['separation_location'] = {
                "city": city,
                "country": country_state,
                "code": code,
            }

    return res


def fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(data={}):
    if isinstance(data, list):
        data = data[0]
    return {
        "emp_seq_num": data.get("hruempseqnbr") or data.get("perpiiseqnum") or None,
        "perdet_seqnum": data.get("perdetseqnum"),
        "per_desc": data.get("persdesc"),
        "neu_id": data.get("neuid"),
        "hru_id": data.get("hruid"),
        "last_name": data.get("perpiilastname") or data.get("neulastnm") or None,
        "first_name": data.get("perpiifirstname") or data.get("neufirstnm") or None,
        "middle_name": data.get("perpiimiddlename") or data.get("neumiddlenm") or None,
    }

# aia = agenda item assignment
def fsbid_aia_to_talentmap_aia(data):
    tod_code = pydash.get(data, "asgdtodcode")
    tod_months = pydash.get(data, "asgdtodmonthsnum")
    tod_other_text = pydash.get(data, "asgdtodothertext") # only custom/other TOD should have months and other_text
    tod_short_desc = pydash.get(data, "todshortdesc")
    tod_long_desc = pydash.get(data, "toddesctext")
    is_other_tod = True if (tod_code == 'X') and (tod_other_text) else False
    skills_data = services.get_skills(pydash.get(data, 'position[0]', {}))
    not_applicable = '-'
    pay_plan = pydash.get(data, "position[0].pospayplancode")
    grade = pydash.get(data, "position[0].posgradecode")
    combined_pp_grade = combine_pp_grade(pay_plan, grade, '--')

    return {
        "id": pydash.get(data, "asgdasgseqnum", None),
        # Redundant field - TO DO: Fix backward compatibility issues and remove extra field
        "asg_seq_num": pydash.get(data, "asgdasgseqnum", None),
        "revision_num": data.get("asgdrevisionnum"),
        "pos_title": pydash.get(data, "position[0].postitledesc", None),
        "pos_num": pydash.get(data, "position[0].posnumtext", None),
        "org": pydash.get(data, "position[0].posorgshortdesc", None),
        "eta": pydash.get(data, "asgdetadate", None),
        "ted": not_applicable if tod_long_desc == 'INDEFINITE' else pydash.get(data, "asgdetdteddate", None),
        "tod": tod_code,
        "tod_months": tod_months if is_other_tod else None, # only custom/other TOD should have months and other_text
        "tod_short_desc": tod_other_text if is_other_tod else tod_short_desc,
        "tod_long_desc": tod_other_text if is_other_tod else tod_long_desc,
        "languages": services.parseLanguagesToArr(pydash.get(data, "position[0]", None)),
        "travel_desc": not_applicable,
        "action": not_applicable,
        "is_separation": False,
        "pay_plan": pay_plan,
        "grade": grade,
        "combined_pp_grade": combined_pp_grade,
        "pay_plan_desc": pydash.get(data, "position[0].pospayplandesc", None),
        "skill": skills_data.get("skill_1_representation"),
        "skill_code": skills_data.get("skill_1_code"),
        "skill_secondary": skills_data.get("skill_2_representation"),
        "skill_secondary_code": skills_data.get("skill_2_code"),
        "custom_skills_description": skills_data.get("combined_skills_representation"),
    }

def fsbid_lang_to_talentmap_lang(data):
    lang_code = pydash.get(data, "pllangcode", None)
    speaking_score = pydash.get(data, "pllpcodespeakcode", None)
    reading_score = pydash.get(data, "pllpcodereadcode", None)
    return {
        "lang_code": lang_code,
        "speaking_score": speaking_score,
        "reading_score": reading_score,
        "test_date": pydash.get(data, "pltestdate", None),
        "custom_description": f"{lang_code} {speaking_score or '-'}/{reading_score or '-'} "
    }

def fsbid_cdo_to_talentmap_cdo(data):
    return {
        "first_name": pydash.get(data, "perpiifirstname", None),
        "last_name": pydash.get(data, "perpiilastname", None),
    }

def fsbid_org_to_talentmap_org(data):
    return {
        "org_descr": pydash.get(data, "orgmvgmdescrshort", None),
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


def convert_create_panel_meeting_item_query(query):
    creator_id = pydash.get(query, "hru_id")
    return {
        "pmimiccode": pydash.get(query, "panelMeetingCategory") or "D",
        "pmipmseqnum": int(pydash.get(query, "panelMeetingId")),
        "pmicreateid": creator_id,
        "pmiupdateid": creator_id,
    }
    

def convert_edit_panel_meeting_item_query(query):
    refData = query.get("refData")
    return {
        "pmipmseqnum": int(query.get("panelMeetingId")),
        "pmiseqnum": refData.get("pmi_seq_num"),
        "pmiofficialitemnum": refData.get("pmi_official_item_num"),
        "pmiaddendumind": refData.get("pmi_addendum_ind"),
        "pmilabeltext": refData.get("pmi_label_text"),
        "pmimiccode": query.get("panelMeetingCategory"),
        "pmicreateid": refData.get("pmi_create_id"),
        "pmicreatedate": refData.get("pmi_create_date", "").replace("T", " "),
        "pmiupdateid": query.get("hru_id"),
        "pmiupdatedate": refData.get("pmi_update_date", "").replace("T", " "),
    }


def convert_create_agenda_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    user_id = pydash.get(query, "hru_id")

    return {
        "aipmiseqnum": query.get("pmiseqnum", ""),
        "empseqnbr": query.get("personId", ""),
        "aiperdetseqnum": query.get("personDetailId", ""),
        "aiaiscode": query.get("agendaStatusCode", ""),
        "aitodcode": query.get("combinedTod", ""),
        "aicombinedtodmonthsnum": query.get("combinedTodMonthsNum", ""),
        "aicombinedtodothertext": query.get("combinedTodOtherText", ""),
        "aiasgseqnum": query.get("assignmentId", ""),
        "aiasgdrevisionnum": query.get("assignmentVersion"),
        "aicombinedremarktext": None,
        "aicorrectiontext": None,
        "ailabeltext": None,
        "aisorttext": None,
        "aicreateid": user_id,
        "aicreatedate": None,
        "aiupdateid": user_id,
        "aiupdatedate": None,
        "aiseqnumref": None,
        "aiitemcreatorid": user_id,
    }


def convert_edit_agenda_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    refData = query.get("refData", {})
    create_date = refData.get("creator_date", "").replace("T", " ")
    update_date = refData.get("modifier_date", "").replace("T", " ")
    return {
        "aiseqnum": refData.get("id"),
        "aipmiseqnum": refData.get("pmi_seq_num"),
        "empseqnbr": query.get("personId", ""),
        "aiperdetseqnum": query.get("personDetailId", ""),
        "aiaiscode": query.get("agendaStatusCode", ""),
        "aitodcode": query.get("combinedTod", ""),
        "aicombinedtodmonthsnum": query.get("combinedTodMonthsNum", ""),
        "aicombinedtodothertext": query.get("combinedTodOtherText", ""),
        "aiasgseqnum": query.get("assignmentId", ""),
        "aiasgdrevisionnum": query.get("assignmentVersion"),
        "aicombinedremarktext": None,
        "aicorrectiontext": None,
        "ailabeltext": None,
        "aisorttext": None,
        "aicreateid": refData.get("creator_name"),
        "aicreatedate": create_date,
        "aiupdateid": query.get("hru_id"),
        "aiupdatedate": update_date,
        "aiseqnumref": None,
        "aiitemcreatorid": refData.get("creator_name")
    }


def convert_agenda_item_leg_query(query, leg={}):
    '''
    Converts TalentMap query into FSBid query
    '''

    user_id = pydash.get(query, "hru_id")

    tod_code = pydash.get(leg, "tod", ""),
    tod_long_desc = pydash.get(leg, "tod_long_desc")
    is_other_tod = True if (tod_code == 'X') and (tod_long_desc) else False
    tod_months = pydash.get(leg, "tod_months")
    ted = (leg.get("ted") or '').replace("T", " ")
    eta = (leg.get("eta") or '').replace("T", " ")

    return {
        "ailaiseqnum": pydash.get(query, "aiseqnum"),
        "aillatcode": pydash.get(leg, "action_code", ""),
        "ailtfcd": pydash.get(leg, "travel_code", ""),
        "ailcpid": int(pydash.get(leg, "ail_cp_id") or 0) or None,
        "ailempseqnbr": int(pydash.get(query, "personId") or 0) or None,
        "ailperdetseqnum": int(pydash.get(query, "personDetailId") or 0) or None,
        "ailposseqnum": int(pydash.get(leg, "ail_pos_seq_num") or 0) or None,
        "ailtodcode": pydash.get(leg, "tod", ""),
        "ailtodmonthsnum": tod_months if is_other_tod else None, # only custom/other TOD should pass back months and other_text
        "ailtodothertext": tod_long_desc if is_other_tod else None, # only custom/other TOD should pass back months and other_text
        "ailetadate": eta.split(".000Z")[0],
        "ailetdtedsepdate": ted.split(".000Z")[0],
        "aildsccd": pydash.get(leg, "separation_location.code") or None,
        "ailcitytext": pydash.get(leg, "separation_location.city") or None,
        "ailcountrystatetext": pydash.get(leg, "separation_location.country") or None,
        "ailusind": None,
        "ailemprequestedsepind": None,
        "ailcreateid": user_id,
        "ailupdateid": user_id,
        "ailasgseqnum": int(pydash.get(leg, "ail_asg_seq_num") or 0) or None,
        "ailasgdrevisionnum": int(pydash.get(leg, "ail_asgd_revision_num") or 0) or None,
        "ailsepseqnum": None,
        "ailsepdrevisionnum": None,
    }


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


def get_agenda_ref_remarks(query, jwt_token):
    '''
    Get agenda reference remarks
    '''
    args = {
        "uri": "references/remarks",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_remarks_ref,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_remarks = services.send_get_request(
        **args
    )

    return agenda_remarks


def fsbid_to_talentmap_agenda_remarks(data):
    return {
        "seq_num": data.get("rmrkseqnum"),
        "rc_code": data.get("rmrkrccode"),
        "order_num": data.get("rmrkordernum"),
        "short_desc_text": data.get("rmrkshortdesctext"),
        "mutually_exclusive_ind": data.get( "rmrkmutuallyexclusiveind"),
        "text": data.get("rmrktext"),
        "ref_text": data.get("refrmrktext"),
        "active_ind": data.get("rmrkactiveind"),
        "remark_inserts": data.get("RemarkInserts"),
        "user_remark_inserts": data.get("refrmrkinsertions"),
        "air_ai_seq_num": data.get("airaiseqnum"),
        "air_rmrk_seq_num": data.get("airrmrkseqnum"),
        "air_remark_text": data.get("airremarktext"),
        "air_complete_ind": data.get("aircompleteind"),
        "air_create_id": data.get("aircreateid"),
        "air_create_date": data.get("aircreatedate"),
        "air_update_id": data.get("airupdateid"),
        "air_update_date": data.get("airupdatedate"),
    }



def fsbid_to_talentmap_agenda_remarks_ref(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = [
        'seq_num', 
        'rc_code', 
        'order_num', 
        'short_desc_text', 
        'mutually_exclusive_ind', 
        'text', 
        'active_ind', 
        'remark_inserts', 
        'ref_text', 
        'update_date',
        'update_id',
        'create_date',
        'create_id',
    ]

    add_these = []

    cols_mapping = {
        'seq_num': 'rmrkseqnum',
        'rc_code': 'rmrkrccode',
        'order_num': 'rmrkordernum',
        'short_desc_text': 'rmrkshortdesctext',
        'mutually_exclusive_ind': 'rmrkmutuallyexclusiveind',
        'text': 'rmrktext',
        'ref_text': 'rmrktext',
        'active_ind': 'rmrkactiveind',
        'update_date': 'rmrkupdatedate',
        'update_id': 'rmrkupdateid',
        'create_date': 'rmrkcreatedate',
        'create_id': 'rmrkcreateid',
        'remark_inserts': 'RemarkInserts'
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
        "mapping_function": fsbid_to_tmap_agenda_leg_action_types,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_leg_action_types = services.send_get_request(
        **args
    )

    return agenda_leg_action_types

def fsbid_to_tmap_agenda_leg_action_types(data):
    separation_types = ['H', 'M', 'N', 'O', 'P']
    code = data.get('latcode')

    return {
        'code': code,
        'abbr_desc_text': data.get('latabbrdesctext'),
        'desc_text': data.get('latdesctext'),
        'is_separation': True if code in separation_types else False,
    }


def convert_agendas_by_panel_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    values = {
        "rp.pageNum": int(0),
        "rp.pageRows": int(0),
        "rp.orderBy": 'pmiofficialitemnum',
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_agendas_by_panel(pk, jwt_token):
    '''
    Get agendas for panel meeting
    '''
    skillUrl = f"{API_ROOT}/v1/references/skills"
    skills = requests.get(skillUrl, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    skills_lookup = {}
    for skill in skills["Data"]:
            skills_lookup[skill["skl_code"]] = skill["skill_descr"]
    args = {
        "uri": f"{pk}/agendas",
        "query": {},
        "query_mapping_function": convert_agendas_by_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_single_agenda_item_to_talentmap_single_agenda_item, ref_skills=skills_lookup),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }
    agendas_by_panel = services.send_get_request(
        **args
    )

    # get vice data to add to agendas_by_panel
    pos_seq_nums = []
    for agenda in agendas_by_panel["results"]:
        legs = pydash.get(agenda, "legs")
        for leg in legs:
            if ('ail_pos_seq_num' in leg) and (leg["ail_pos_seq_num"] is not None):
                pos_seq_nums.append(leg["ail_pos_seq_num"])
    vice_lookup = get_vice_data(pos_seq_nums, jwt_token)

    for agenda in agendas_by_panel["results"]:
        legs = pydash.get(agenda, "legs")
        # append vice data to add to agendas_by_panel
        for leg in legs:
            if 'ail_pos_seq_num' in leg:
                if leg["is_separation"]:
                    leg["vice"] = {} 
                else:
                    leg["vice"] = vice_lookup.get(leg["ail_pos_seq_num"]) or {}
    return agendas_by_panel

def get_agendas_by_panel_export(pk, jwt_token, host=None):
    '''
    Get agendas for panel meeting export
    '''
    mapping_subset = {
        'default': 'None Listed',
        'wskeys': {
            'agendaAssignment[0].position[0].postitledesc': {},
            'agendaAssignment[0].position[0].posnumtext': {
                'transformFn': lambda x: smart_str("=\"%s\"" % x),
            },
            'agendaAssignment[0].position[0].posorgshortdesc': {},
            'agendaAssignment[0].asgdetadate': {
                'transformFn': services.process_dates_csv,
            },
            'agendaAssignment[0].asgdetdteddate': {
                'transformFn': services.process_dates_csv,
            },
            'agendaAssignment[0].asgdtoddesctext': {},
            'agendaAssignment[0].position[0].posgradecode': {
                'transformFn': lambda x: smart_str("=\"%s\"" % x),
            },
            'Panel[0].pmddttm': {
                'transformFn': services.process_dates_csv,
            },
            'aisdesctext': {},
            'remarks': {
                'transformFn': services.process_remarks_csv,
            },
        }
    }
    args = {
        "uri": f"{pk}/agendas",
        "query": {},
        "query_mapping_function": convert_agendas_by_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.csv_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
        "host": host,
        "use_post": False,
    }

    data = services.send_get_request(**args)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=panel_meeting_agendas_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    writer.writerow([
        smart_str(u"Position Title"),
        smart_str(u"Position Number"),
        smart_str(u"Org"),
        smart_str(u"ETA"),
        smart_str(u"TED"),
        smart_str(u"TOD"),
        smart_str(u"Grade"),
        smart_str(u"Panel Date"),
        smart_str(u"Status"),
        smart_str(u"Remarks"),
    ])

    writer.writerows(data['results'])

    return response

def get_vice_data(pos_seq_nums, jwt_token):
    args = {
        "uri": "v1/vice-positions/",
        "jwt_token": jwt_token,
        "query": pos_seq_nums,
        "query_mapping_function": vice_query_mapping,
        "mapping_function": None,
        "count_function": None,
        "base_url": "",
        "host": None,
        "api_root": API_ROOT
    }
    vice_req = services.send_get_request(
        **args
    )
    vice_data = pydash.get(vice_req, 'results')

    vice_lookup = {}
    for vice in vice_data or []:
        if "pos_seq_num" in vice:
            pos_seq = vice["pos_seq_num"]
            # check for multiple incumbents in same postion
            if pos_seq in vice_lookup:
                vice_lookup[pos_seq] = {
                    "pos_seq_num": pos_seq,
                    "emp_first_name": "Multiple",
                    "emp_last_name": "Incumbents"
                }
            else:
                vice_lookup[pos_seq] = vice

    return vice_lookup

def vice_query_mapping(pos_seq_nums):
    pos_seq_nums_string = ','.join(map(lambda x: str(x), list(set(pos_seq_nums))))
    filters = services.convert_to_fsbid_ql([
        {'col': 'pos_seq_num', 'com': 'IN', 'val': pos_seq_nums_string},
    ])
    values = {
        "rp.filter": filters,
        "rp.pageNum": int(0),
        "rp.pageRows": int(0),
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)
