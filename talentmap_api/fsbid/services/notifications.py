import logging
from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import service_response


logger = logging.getLogger(__name__)

# ======================== Get Note Cable ========================

def get_note_cable(data, jwt_token):
    '''
    Gets Note Cable
    '''
    args = {
        "proc_name": "qry_getNoteCable",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT100",
        "request_body": data,
        "request_mapping_function": get_note_cable_req_mapping,
        "response_mapping_function": get_note_cable_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def get_note_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_ASG_SEQ_NUM": request.get("I_ASG_SEQ_NUM"),
        "I_ASGD_REVISION_NUM": request.get("I_ASGD_REVISION_NUM"),
        "I_SEP_SEQ_NUM": "",
        "I_SEPD_REVISION_NUM": "",
    }

def get_note_cable_res_mapping(response):
    def success_mapping(x):
        return list(x.get("QRY_GETNOTECABLE_REF"))
    return service_response(response, 'Note Cable', success_mapping)

# ======================== Get Cable ========================

def get_cable(data, jwt_token):
    '''
    Gets Cable
    '''
    args = {
        "proc_name": "qry_getcable",
        "package_name": "PKG_WEBAPI_WRAP_SPRINT100",
        "request_body": data,
        "request_mapping_function": get_cable_req_mapping,
        "response_mapping_function": get_cable_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def get_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_NM_SEQ_NUM": request.get("I_NM_SEQ_NUM"),
        "I_NM_NOTIFICATION_IND": request.get("I_NM_NOTIFICATION_IND"),
    }

def get_cable_res_mapping(response):
    def success_mapping(x):
        return {
            "O_LAST_SENT_DATE": x.get("O_LAST_SENT_DATE"),
            "O_EOPF_DIRECTORY": x.get("O_EOPF_DIRECTORY"),
            "O_USER_ENVIRONMENT": x.get("O_USER_ENVIRONMENT"),
            "QRY_CABLE_REF": list(x.get("QRY_CABLE_REF")),
            "QRY_APPR_ORIGINATOR": list(x.get("QRY_APPR_ORIGINATOR")),
            "QRY_ROUTING_DISTRO": list(x.get("QRY_ROUTING_DISTRO")),
        }
    return service_response(response, 'Cable', success_mapping)

# ======================== Get Note Cable References ========================

def get_note_cable_ref(data, jwt_token):
    '''
    Get Note Cable Reference Data
    '''
    args = {
        "proc_name": 'qry_modNoteCable',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": get_note_cable_ref_req_mapping,
        "response_mapping_function": get_note_cable_ref_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def get_note_cable_ref_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_NM_SEQ_NUM": request.get("I_NM_SEQ_NUM"),
    }

def get_note_cable_ref_res_mapping(data):
    def success_mapping(x):
        return {
            "QRY_ASG_REF": list(x.get("QRY_ASG_REF")),
            "QRY_CABLE_REF": list(x.get("QRY_CABLE_REF")),
            "QRY_PARA_REF": list(x.get("QRY_PARA_REF")),
            "QRY_DT_REF": list(x.get("QRY_DT_REF")),
            "QRY_PT_REF": list(x.get("QRY_PT_REF")),
            "QRY_POST_REF": list(x.get("QRY_POST_REF")),
            "QRY_ORGS_REF": list(x.get("QRY_ORGS_REF")),
            "QRY_NMD_REF": list(x.get("QRY_NMD_REF")),
        }
    return service_response(data, 'Note Cable Reference', success_mapping)

# ======================== Edit Note Cable ========================

def edit_note_cable(data, jwt_token):
    '''
    Edit Note Cable
    '''
    args = {
        "proc_name": 'act_modNoteMemoAll',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": edit_note_cable_req_mapping,
        "response_mapping_function": edit_note_cable_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def edit_note_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_NM_SEQ_NUM": "",
        "I_HDR_NME_SEQ_NUM": request.get('I_HDR_NME_SEQ_NUM'),
        "I_HDR_CLOB_LENGTH": request.get('I_HDR_CLOB_LENGTH'),
        "I_HDR_NME_OVERRIDE_CLOB": request.get('I_HDR_NME_OVERRIDE_CLOB'),
        "I_HDR_NME_UPDATE_ID": request.get('I_HDR_NME_UPDATE_ID'),
        "I_HDR_NME_UPDATE_DATE": request.get('I_HDR_NME_UPDATE_DATE'),
        "I_HDR_NME_CLEAR_IND": request.get('I_HDR_NME_CLEAR_IND'),
        "I_ASG_NME_SEQ_NUM": "",
        "I_ASG_NMAS_SEQ_NUM": "",
        "I_ASG_NMAS_UPDATE_ID": "",
        "I_ASG_NMAS_UPDATE_DT": "",
        "I_PARA_NME_SEQ_NUM": "",
        "I_PARA_NOTP_CODE": "",
        "I_PARA_NME_UPDATE_ID": "",
        "I_PARA_NME_UPDATE_DATE": "",
        "I_DIST_NME_SEQ_NUM": "",
        "I_DIST_NME_UPDATE_ID": "",
        "I_DIST_NME_UPDATE_DATE": "",
        "I_ACT_NME_SEQ_NUM": "",
        "I_ACT_NME_UPDATE_ID": "",
        "I_ACT_NME_UPDATE_DATE": "",
        "I_INFO_NME_SEQ_NUM": "",
        "I_INFO_NME_UPDATE_ID": "",
        "I_INFO_NME_UPDATE_DATE": "",
        "I_INC_IND": "",
        "I_NMD_SEQ_NUM": "",
        "I_DT_CODE": "",
        "I_PT_CODE": "",
        "I_ORG_CODE": "",
        "I_CP_SEQ_NUM": "",
        "I_NMD_SLUG_TEXT": "",
        "I_NMD_UPDATE_ID": "",
        "I_NMD_UPDATE_DATE": "",
    }

def edit_note_cable_res_mapping(data):
    return service_response(data, 'Edit Note Cable')

# ======================== Rebuild Note Cable ========================

def rebuild_note_cable(data, jwt_token):
    '''
    Rebuild Note Cable
    '''
    args = {
        "proc_name": 'act_modNoteMemoRebuild',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": rebuild_note_cable_req_mapping,
        "response_mapping_function": rebuild_note_cable_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def rebuild_note_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_NM_SEQ_NUM": request.get('I_NM_SEQ_NUM'),
        "I_NME_SEQ_NUM": request.get('I_NME_SEQ_NUM'),
        "I_NME_UPDATE_ID": request.get('I_NME_UPDATE_ID'),
        "I_NME_UPDATE_DATE": request.get('I_NME_UPDATE_DATE'),
    }

def rebuild_note_cable_res_mapping(data):
    return service_response(data, 'Rebuild Note Cable')

# ======================== Store Note Cable ========================

def store_note_cable(data, jwt_token):
    '''
    Store Note Cable
    '''
    args = {
        "proc_name": 'act_storeTMOne',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": store_note_cable_req_mapping,
        "response_mapping_function": store_note_cable_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def store_note_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "I_NM_SEQ_NUM": request.get('I_NM_SEQ_NUM'),
        "I_NOTE_TYPE": "",
    }

def store_note_cable_res_mapping(data):
    return service_response(data, 'Store Note Cable')

# ======================== Send Note Cable ========================

def send_note_cable(data, jwt_token):
    '''
    Send Note Cable
    '''
    args = {
        "proc_name": 'act_mod_sendcable',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_mapping_function": send_note_cable_req_mapping,
        "response_mapping_function": send_note_cable_res_mapping,
        "jwt_token": jwt_token,
        "request_body": data,
    }
    return services.send_post_back_office(
        **args
    )

def send_note_cable_req_mapping(request):
    return {
        "PV_API_VERSION_I": "",
        "PV_AD_ID_I": "",
        "PV_NM_SEQ_NUM_I": request.get('PV_NM_SEQ_NUM_I'),
        "PV_FILE_NAME_I": "",
        "PV_NOTE_TYPE_I": "",
        "PV_RETURN_CODE_O": "",
    }

def send_note_cable_res_mapping(data):
    return service_response(data, 'Send Note Cable')
