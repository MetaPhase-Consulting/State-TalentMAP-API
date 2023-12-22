import logging

from django.conf import settings
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL


def get_assignment_cycles_data(jwt_token, request):
    '''
    Gets the Data for the Assignment Cycle Management Page
    '''
    args = {
        "proc_name": 'qry_lstassigncycles',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT100',
        "request_body": request,
        "request_mapping_function": assignment_cycles_req_mapping,
        "response_mapping_function": assignment_cycles_res_mapping,
        "jwt_token": jwt_token,
    }
    return services.send_post_back_office(
        **args
    )


def assignment_cycles_req_mapping(request):
    mapped_request = {
        "PV_API_VERSION_I": "",
        'PV_AD_ID_I': '',
    }
    return mapped_request


def assignment_cycles_res_mapping(data):
    def results_mapping(x):
        return {
            'id': x.get('CYCLE_ID') or None,
            'name': x.get('CYCLE_NM_TXT') or None,
            'status': x.get('CS_DESCR_TXT') or None,
            'category': x.get('CC_DESCR_TXT') or None,
            'begin_date': x.get('CD_BGN_DT') or None,
            'end_date': x.get('CD_END_DT') or None,
            'excl_position': x.get('CYCLE_EXCLUSIVE_POS_FLG') or None,
            'post_view': x.get('CYCLE_POST_VIEWABLE_IND') or None,
        }
    return list(map(results_mapping, data.get('QRY_LSTASSIGNCYCLES_REF')))
