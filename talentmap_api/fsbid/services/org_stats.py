import logging
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

def get_org_stats(query, jwt_token):
    print('get_org_stats WE MADE IT HERRRRRREEEEEEE')
    print(query)
    '''
    Get Org Stats
    '''
    args = {
        "proc_name": 'qry_lstfsbidSearch',
        "package_name": 'PKG_WEBAPI_WRAP',
        "request_mapping_function": org_stats_req_mapping,
        "response_mapping_function": org_stats_res_mapping,
        "jwt_token": jwt_token,
        "request_body": query,
    }
    return services.send_post_back_office(
        **args
    )
def org_stats_req_mapping(request):
    return {
        'pv_api_version_i': '',
        'pv_ad_id_i': '',
        'i_cycle_id': '',
        'i_bureau_id': '',
        'i_org_code': '',
    }
def org_stats_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error('FSBid call for Org Stat failed.')
        return None
        
    def org_stats_map(x):
        # to flag object with all null values and prevent .strip on it
        if x.get('HRU_ID') is None:
            return {}

        userBureauNames = x.get('BUREAU_NAME_LIST', '').strip() or ''
        userBureauNames = userBureauNames.split(',') if userBureauNames else []

        userBureauCodes = x.get('PARM_VALUES', '').strip() or ''
        userBureauCodes = userBureauCodes.split(',') if userBureauCodes else []

        return {
            'pvId': x.get('PV_ID'),
            'name': services.remove_nmn(x.get('EMP_FULL_NAME')),
            'userBureauNames': userBureauNames,
            'empSeqNum': x.get('EMP_SEQ_NBR'),
            'hruId': x.get('HRU_ID'),
            'userBureauCodes': userBureauCodes,
        }

    result = map(org_stats_map, data.get('QRY_LSTORGSTATS_REF'))

    return list(filter(lambda x: x != {}, result))
