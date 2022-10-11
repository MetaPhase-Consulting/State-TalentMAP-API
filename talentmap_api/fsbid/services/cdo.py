import logging
import jwt
import pydash
from django.conf import settings
from talentmap_api.common.common_helpers import get_avatar_url

CLIENTS_API_URL = settings.CLIENTS_API_URL

logger = logging.getLogger(__name__)


def cdo(jwt_token):
    '''
    Get All Internal CDAs
    '''
    from talentmap_api.fsbid.services.common import get_fsbid_results
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&request_params.rl_cd=CDO&request_params.rl_cd=CDO3"
    response = get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email, False, CLIENTS_API_URL)
    response = list(response)
    response = [d for i, d in enumerate(response) if d['id'] not in [x['id'] for x in response[i + 1:]]] # dedup
    response = pydash.order_by(response, ['name'])
    return response


def single_cdo(jwt_token=None, perdet_seq_num=None):
    '''
    Get a single Internal CDA
    '''
    from talentmap_api.fsbid.services.common import get_fsbid_results
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&request_params.rl_cd=CDO&request_params.rl_cd=CDO3&request_params.perdet_seq_num={perdet_seq_num}"
    response = get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email, False, CLIENTS_API_URL)
    cdos = None

    if response is not None:
        cdos = list(response)

    if cdos and len(cdos) > 0:
        try:
            CDO = cdos[0]
            initials = "".join([x for x in CDO['email'] if x.isupper()][:2][::-1])
            CDO['initials'] = initials
            avatar = get_avatar_url(CDO['email'])
            CDO['avatar'] = avatar
        except:
            CDO = {}
    else:
        CDO = {}
    return CDO


def fsbid_cdo_list_to_talentmap_cdo_list(data):
    fullname = data.get("fullname", None)
    if fullname:
        fullname = fullname.rstrip(' NMN')

    return {
        "id": data.get("hru_id", None),
        "name": fullname,
        "email": data.get("email", None),
        "isCurrentUser": data.get("isCurrentUser", None),
    }
