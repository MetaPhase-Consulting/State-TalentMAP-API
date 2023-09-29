import logging
from urllib.parse import urlencode, quote
import jwt
import pydash
from django.conf import settings

from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services import common as services

BUREAU_EXCEPTION_LIST_ROOT = settings.BUREAU_EXCEPTION_LIST_API_URL

logger = logging.getLogger(__name__)

def get_bureau_exception_list(query, jwt_token):
    '''
    Gets Bureau Exception List
    '''
    args = {
        "proc_name": 'qry_modPBureauExcpt',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": bureau_exception_list_req_mapping,
        "response_mapping_function": bureau_exception_list_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )

def bureau_exception_list_req_mapping(request):
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

def bureau_exception_list_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Bureau Exception List failed.")
        return None

    def pub_pos_map(x):
        return {
            'positionNumber': x.get('POS_NUM_TXT'),
            'skill': services.format_desc_code(x.get('SKL_DESC_POS'), x.get('SKL_CODE_POS')),
            'positionTitle': x.get('POS_TITLE_TXT'),
            'bureau': x.get('BUR_SHORT_DESC'),
            'org': services.format_desc_code(x.get('ORGS_SHORT_DESC'), x.get('ORG_CODE')),
            'grade': x.get('GRD_CD'),
            'status': x.get('PUBS_CD'),
            'language': x.get('LANG_DESCR_TXT'),
            'payPlan': x.get('PPL_CODE'),
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

    return list(map(pub_pos_map, data.get('QRY_MODBIDEXCP_REF')))