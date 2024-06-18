import logging
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response


logger = logging.getLogger(__name__)

# ======================== Get Position Classifications ========================

def get_position_classifications(pk, jwt_token):
    '''
    Gets Position Classifications for a position
    '''
    args = {
        "proc_name": "qry_modPosClasses",
        "package_name": "PKG_WEBAPI_WRAP",
        "request_body": pk,
        "request_mapping_function": position_classifications_request_mapping,
        "response_mapping_function": position_classifications_response_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def position_classifications_request_mapping(request):
    return {
        "PV_API_VERSION_I": '',
        "PV_AD_ID_I": '',
        "I_GRD_CD": '',
        "I_SKL_CODE_POS": '',
        "I_ORG_CODE": '',
        "I_POS_NUM_TXT": request,
        "I_POS_OVRSES_IND": '',
        "I_PS_CD": '',
        "I_BUREAU_CD": '',
        "I_PUBS_CD": '',
        "I_JC_ID": '',
        "I_ORDER_BY": '',
        "I_PCT_CODE": ''
    }

def position_classifications_response_mapping(response):
    def position_classifications(x):
        return {
            'code': x.get('PCT_CODE'),
            'description': x.get('PCT_DESC_TEXT'),
            'short_description': x.get('PCT_SHORT_DESC_TEXT'),
        }
    def position_classifications_selection(x):
        return {
            'code': x.get('PCT_CODE'),
            'value': x.get('INC_IND'),
            'user_id': x.get('POSC_USERID'),
            'date': x.get('POSC_TMSMP_ID'),
        }
    def success_mapping(x):
        return {
            'positionClassifications': list(map(position_classifications, x.get('QRY_PCT_REF'))),
            'classificationSelections': list(map(position_classifications_selection, x.get('QRY_MODPOSCLASSES_REF'))),
        }
    return service_response(response, 'Panel Classifications Data', success_mapping)

# ======================== Edit Position Classifications ========================

def edit_position_classifications(data, jwt_token):
    '''
    Edit a Position's Position Classifications
    '''
    args = {
        "proc_name": 'act_modPosClasses',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": edit_positon_classifications_req_mapping,
        "response_mapping_function": edit_positon_classifications_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_positon_classifications_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_INC_IND": request.get('values'),
        "I_POS_SEQ_NUM": request.get('id'),
        "I_PCT_CODE": request.get('codes'),
        "I_POSC_UPDATE_ID": request.get('updater_ids'),
        "I_POSC_UPDATE_DATE": request.get('updated_dates'),
        "O_RETURN_CODE": "",
        "QRY_ACTION_DATA": "",
        "QRY_ERROR_DATA": ""
    }

def edit_positon_classifications_res_mapping(data):
    return service_response(data, 'Post Position Classifications Edit')