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