import logging
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response


logger = logging.getLogger(__name__)

# ======================== Get Bidding Tool List ========================

def get_bidding_tools(data, jwt_token):
    '''
    Get Bidding Tool List
    '''
    args = {
        "proc_name": "qry_lstbiddingtool",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT101",
        "request_body": data,
        "request_mapping_function": bidding_tools_request_mapping,
        "response_mapping_function": bidding_tools_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def bidding_tools_request_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def bidding_tools_response_mapping(response):
    def bidding_tools(x):
        return {
            'location_code': x.get('POS_LOCATION_CODE'),
            'dsv_name': x.get('DSV_NAME'),
            'bt_ind': x.get('BT_IND'),
        }
    def success_mapping(x):
        return list(map(bidding_tools, x.get('QRY_LSTBIDDINGTOOL_REF')))
        
    return service_response(response, 'Bidding Tool List Data', success_mapping)


# ======================== Get Bidding Tool ========================

def get_bidding_tool(pk, jwt_token):
    '''
    Get Bidding Tool
    '''
    args = {
        "proc_name": "qry_lstbiddingtool",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT101",
        "request_body": pk,
        "request_mapping_function": bidding_tool_request_mapping,
        "response_mapping_function": bidding_tool_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def bidding_tool_request_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_dsc_cd': request,
    }

def bidding_tool_response_mapping(response):
    def locations(x):
        return {
            'code': x.get('POS_LOCATION_CODE'),
            'state_country': x.get('GSA_STATE_COUNTRY'),
            'dsv_nm': x.get('DSV_NM'),
        }
    def statuses(x):
        return {
            'code': x.get('BTS_CODE'),
            'description': x.get('BTS_DESC_TEXT'),
        }
    def tods(x):
        return {
            'code': x.get('TOD_CODE'),
            'description': x.get('TOD_DESC_TEXT'),
        }
    def unaccompanied_statuses(x):
        return {
            'code': x.get('US_CODE'),
            'description': x.get('US_DESC_TEXT'),
        }
    def housing_types(x):
        return {
            'code': x.get('HT_CODE'),
            'description': x.get('HT_DESC_TEXT'),
        }
    def quarters_types(x):
        return {
            'code': x.get('QT_CODE'),
            'description': x.get('QT_DESC_TEXT'),
        }
    def ehcps(x):
        return {
            'code': x.get('EHCP_CODE'),
            'description': x.get('EHCP_SHORT_DESC_TEXT'),
        }
    def success_mapping(x):
        return {
            'snd': x.get('O_BT_SERVICE_NEEDS_DIFF_FLG'),
            'hds': x.get('O_BT_MOST_DIFF_TO_STAFF_FLG'),
            'rr_point': x.get('O_BT_REST_RELAXATION_PNT_TEXT'),
            'apo_fpo_dpo': x.get('O_BT_APO_OR_FPO_FLG'),
            'cola': x.get('O_BT_COST_OF_LIVING_ADJUST_NUM'),
            'differential_rate': x.get('O_BT_DIFFERENTIAL_RATE_NUM'),
            'danger_pay': x.get('O_BT_DANGER_PAY_NUM'),
            'medical': x.get('O_BT_MEDICAL_REMARKS_TEXT'),
            'remarks': x.get('O_BT_REMARKS_TEXT'),
            'climate_zone': x.get('O_BT_CLIMATE_ZONE_NUM'),
            'consumable_allowance': x.get('O_BT_CONSUMABLE_ALLOWANCE_FLG'),
            'fm_fp': x.get('O_BT_FOREIGN_MADE_PROV_FLG'),
            'quarters_remark': x.get('O_BT_QUARTERS_REMARK_TEXT'),
            'special_ship_allowance': x.get('O_BT_SPEC_SHIP_ALLOW_TEXT'),
            'school_year': x.get('O_BT_SCHOOL_YEAR_TEXT'),
            'grade_education': x.get('O_BT_GRADE_EDUCATION_TEXT'),
            'efm_employment': x.get('O_BT_EFM_EMPLOYMENT_TXT'),
            'inside_efm_employment': x.get('O_BT_INSIDE_EFM_EMPLOYMENT_FLG'),
            'outside_efm_employment': x.get('O_BT_OUTSIDE_EFM_EMPLOYMENT_FLG'),

            'location': x.get('O_DSC_CD'),
            'unaccompanied_status': x.get('O_US_CODE'),
            'status': x.get('O_BTS_CODE'),
            'quarters': x.get('O_QT_CODE'),
            'housing': x.get('O_HT_CODE'),
            'efm_issues': x.get('O_EHCP_CODE'),
            'tod': x.get('O_TOD_CODE'),
            
            'updater_id': x.get('O_BT_UPDATE_ID'),
            'updated_date': x.get('O_BT_UPDATE_DATE'),

            'locations': list(map(locations, x.get('QRY_LSTLOCATIONS_REF'))),
            'statuses': list(map(statuses, x.get('QRY_LSTSTATUS_REF'))),
            'tods': list(map(tods, x.get('QRY_LSTTODS_REF'))),
            'unaccompanied_statuses': list(map(unaccompanied_statuses, x.get('QRY_LSTUNACCOMPSTATUS_REF'))),
            'housing_types': list(map(housing_types, x.get('QRY_LSTHOUSINGTYPE_REF'))),
            'quarters_types': list(map(quarters_types, x.get('QRY_LSTQUARTERSTYPE_REF'))),
            'ehcps': list(map(ehcps, x.get('QRY_LSTEHCP_REF'))),
        }
    return service_response(response, 'Bidding Tool Data', success_mapping)


# ======================== Delete Bidding Tool ========================

def delete_bidding_tool(data, jwt_token):
    '''
    Delete Bidding Tool
    '''
    args = {
        "proc_name": "act_delbiddingtool",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT101",
        "request_body": data,
        "request_mapping_function": delete_bidding_tool_request_mapping,
        "response_mapping_function": delete_bidding_tool_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def delete_bidding_tool_request_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_dsc_cd': request.get('location'),
        'I_BT_UPDATE_ID': request.get('updater_id'),
        'I_BT_UPDATE_DATE': request.get('updated_date')
    }

def delete_bidding_tool_response_mapping(response):
    return service_response(response, 'Bidding Tool Delete')


# ======================== Create Bidding Tool ========================

def base_action_request(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
        'i_dsc_cd': request.get('location'),
        'i_bt_service_needs_diff_flg': request.get('snd'),
        'i_bts_code': request.get('status'),
        'i_bt_most_diff_to_staff_flg': request.get('hds'),
        'i_tod_code': request.get('tod'),
        'i_bt_rest_relaxation_pnt_text': request.get('rr_point'),
        'i_us_code': request.get('unaccompanied_status'),
        'i_bt_apo_or_fpo_flg': request.get('apo_fpo_dpo'),
        'i_bt_cost_of_living_adjust_num': request.get('cola'),
        'i_bt_differential_rate_num': request.get('differential_rate'),
        'i_bt_danger_pay_num': request.get('danger_pay'),
        'i_bt_remarks_text': request.get('remarks'),
        'i_bt_climate_zone_num': request.get('climate_zone'),
        'i_ht_code': request.get('housing'),
        'i_qt_code': request.get('quarters'),
        'i_bt_consumable_allowance_flg': request.get('consumable_allowance'),
        'i_bt_quarters_remark_text': request.get('quarters_remark'),
        'i_bt_special_ship_allow_text': request.get('special_ship_allowance'),
        'i_bt_foreign_made_prov_flg': request.get('fm_fp'),
        'i_bt_school_year_text': request.get('school_year'),
        'i_bt_grade_education_text': request.get('grade_education'),
        'i_bt_efm_employment_txt': request.get('efm_employment'),
        'i_bt_inside_efm_employment_flg': request.get('inside_efm_employment'),
        'i_bt_outside_efm_emp_flg': request.get('outside_efm_employment'),
        'i_ehcp_code': request.get('efm_issues'),
        'i_bt_medical_remarks_text': request.get('medical')
    }

def create_bidding_tool(data, jwt_token):
    '''
    Create Bidding Tool
    '''
    args = {
        "proc_name": 'act_addbiddingtool',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_mapping_function": create_bidding_tool_request_mapping,
        "response_mapping_function": create_bidding_tool_response_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def create_bidding_tool_request_mapping(request):
    return base_action_request(request)

def create_bidding_tool_response_mapping(data):
    return service_response(data, 'Bidding Tool Create')

# ======================== Get Bidding Tool Create Data ========================

def get_bidding_tool_create_data(data, jwt_token):
    '''
    Get Bidding Tool Create Data
    '''
    args = {
        "proc_name": "qry_addBiddingTool",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT101",
        "request_body": data,
        "request_mapping_function": bidding_tool_create_data_request_mapping,
        "response_mapping_function": bidding_tool_create_data_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def bidding_tool_create_data_request_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def bidding_tool_create_data_response_mapping(response):
    def locations(x):
        return {
            'code': x.get('POS_LOCATION_CODE'),
            'state_country': x.get('GSA_STATE_COUNTRY'),
            'dsv_nm': x.get('DSV_NM'),
        }
    def statuses(x):
        return {
            'code': x.get('BTS_CODE'),
            'description': x.get('BTS_DESC_TEXT'),
        }
    def tods(x):
        return {
            'code': x.get('TOD_CODE'),
            'description': x.get('TOD_DESC_TEXT'),
        }
    def unaccompanied_statuses(x):
        return {
            'code': x.get('US_CODE'),
            'description': x.get('US_DESC_TEXT'),
        }
    def housing_types(x):
        return {
            'code': x.get('HT_CODE'),
            'description': x.get('HT_DESC_TEXT'),
        }
    def quarters_types(x):
        return {
            'code': x.get('QT_CODE'),
            'description': x.get('QT_DESC_TEXT'),
        }
    def ehcps(x):
        return {
            'code': x.get('EHCP_CODE'),
            'description': x.get('EHCP_SHORT_DESC_TEXT'),
        }
    def success_mapping(x):
        return {
            'locations': list(map(locations, x.get('QRY_LSTLOCATIONS_REF'))),
            'statuses': list(map(statuses, x.get('QRY_LSTSTATUS_REF'))),
            'tods': list(map(tods, x.get('QRY_LSTTODS_REF'))),
            'unaccompanied_statuses': list(map(unaccompanied_statuses, x.get('QRY_LSTUNACCOMPSTATUS_REF'))),
            'housing_types': list(map(housing_types, x.get('QRY_LSTHOUSINGTYPE_REF'))),
            'quarters_types': list(map(quarters_types, x.get('QRY_LSTQUARTERSTYPE_REF'))),
            'ehcps': list(map(ehcps, x.get('QRY_LSTEHCP_REF'))),
        }
    return service_response(response, 'Bidding Tool Create Data', success_mapping)

# ======================== Edit Bidding Tool ========================

def edit_bidding_tool(data, jwt_token):
    '''
    Edit Bidding Tool
    '''
    args = {
        "proc_name": 'act_modbiddingtool',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
        "request_mapping_function": edit_bidding_tool_request_mapping,
        "response_mapping_function": edit_bidding_tool_response_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_bidding_tool_request_mapping(request):
    return {
        **base_action_request(request),
        'I_BT_UPDATE_ID': request.get('updater_id'),
        'I_BT_UPDATE_DATE': request.get('updated_date'),
    }

def edit_bidding_tool_response_mapping(data):
    return service_response(data, 'Bidding Tool Edit')