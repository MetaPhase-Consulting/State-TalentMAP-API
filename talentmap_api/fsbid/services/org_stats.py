import logging
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

def get_org_stats(query, jwt_token):
    '''
    Get Org Stats
    '''
    args = {
        "proc_name": 'qry_lstorgstats',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT101',
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
        'i_cycle_id': request.get('cycles') or 0,
        'i_bureau_cd': request.get('bureaus') or '',
        'i_org_code': request.get('orgs') or '',
    }

def org_stats_res_mapping(data):
    if data is None or data.get('O_RETURN_CODE') != 0:
        logger.error('FSBid call for Org Stat failed.')
        return None
        
    
    def list_org_stats_map(x):
        return {
            'title': x.get('CYCLE_NM_TXT'),
            'bureau_code': x.get('BUREAU_CODE'),
            'bureau_short_desc': x.get('BUR_SHORT_DESC'),
            'org_code': x.get('ORG_CODE'),
            'organization': x.get('ORGS_SHORT_DESC'),
            'total_pos': x.get('ORG_TTL_POS_QTY'),
            'total_filled': x.get('ORG_FILLED_POS_QTY'),
            'total_percent': x.get('ORG_FILLED_POS_PCT'),
            'overseas_pos': x.get('ORG_TTL_POS_OVRS_QTY'),
            'overseas_filled': x.get('ORG_FILLED_POS_OVRS_QTY'),
            'overseas_percent': x.get('ORG_FILLED_POS_OVRS_PCT'),
            'domestic_pos': x.get('ORG_TTL_POS_DMSTC_QTY'),
            'domestic_filled': x.get('ORG_FILLED_POS_DMSTC_QTY'),
            'domestic_percent': x.get('ORG_FILLED_POS_DMSTC_PCT'),
            'total_bids': x.get('ORG_TTL_BIDS_QTY'),
            'total_bidders': x.get('ORG_TTL_BIDDERS_QTY'),
        }

    def list_bureau_stats_map(x):
        return {
            'bureau': f'({x.get("BUREAU_CODE")}) {x.get("BUR_SHORT_DESC")}',
            'bureau_code': x.get('BUREAU_CODE'),
            'bureau_short_desc': x.get('BUR_SHORT_DESC'),
            'total_pos': x.get('BUR_TTL_POS_QTY'),
            'total_filled': x.get('BUR_FILLED_POS_QTY'),
            'total_percent': int((x.get('BUR_FILLED_POS_QTY')/x.get('BUR_TTL_POS_QTY')) * 100) if x.get('BUR_TTL_POS_QTY') else 0,
            'overseas_pos': x.get('BUR_TTL_POS_OVRS_QTY'),
            'overseas_filled': x.get('BUR_FILLED_POS_OVRS_QTY'),
            'overseas_percent': int((x.get('BUR_FILLED_POS_OVRS_QTY')/x.get('BUR_TTL_POS_OVRS_QTY')) * 100) if x.get('BUR_TTL_POS_OVRS_QTY') else 0,
            'domestic_pos': x.get('BUR_TTL_POS_DMSTC_QTY'),
            'domestic_filled': x.get('BUR_FILLED_POS_DMSTC_QTY'),
            'domestic_percent': int((x.get('BUR_FILLED_POS_DMSTC_QTY')/x.get('BUR_TTL_POS_DMSTC_QTY')) * 100) if x.get('BUR_TTL_POS_DMSTC_QTY') else 0,
            'org_count': x.get('ORG_COUNT'),
            'total_bids_qty': x.get('BUR_TTL_BIDS_QTY'),
            'total_bidders_qty': x.get('BUR_TTL_BIDDERS_QTY'),
        }
    
    return {
        'results': list(map(list_org_stats_map, data.get('QRY_LSTORGSTATS_REF'))),
        'bureau_summary': list(map(list_bureau_stats_map, data.get('QRY_LSTBUREAUSTATS_REF'))),
    }

def get_org_stats_filters(jwt_token):
    '''
    Gets Filters for Org Stats Page
    '''
    args = {
        'proc_name': 'qry_lstfsbidSearch',
        'package_name': 'PKG_WEBAPI_WRAP',
        'request_body': {},
        'request_mapping_function': org_stats_filter_req_mapping,
        'response_mapping_function': org_stats_filter_res_mapping,
        'jwt_token': jwt_token,
    }
    return services.send_post_back_office(
        **args
    )

def org_stats_filter_req_mapping(request):
    return {
        'PV_API_VERSION_I': '',
        'PV_AD_ID_I': '',
    }

def org_stats_filter_res_mapping(data):
    if data is None or (data['O_RETURN_CODE'] and data['O_RETURN_CODE'] is not 0):
        logger.error(f"Fsbid call for Org Stats filters failed.")
        return None

    def cycle_map(x):
        return {
            'code': x.get('CYCLE_ID'),
            'description': x.get('CYCLE_NM_TXT'),
        }
    def bureau_map(x):
        return {
            'description': x.get('ORGS_SHORT_DESC'),
        }
    def org_map(x):
        return {
            'code': x.get('ORG_CODE'),
            'description': f"{x.get('ORGS_SHORT_DESC')} ({x.get('ORG_CODE')})",
        }


    return {
        'cycleFilters': list(map(cycle_map, data.get('QRY_LSTASSIGNCYCLE_DD_REF'))),
        'bureauFilters': list(map(bureau_map, data.get('QRY_LSTBUREAUS_DD_REF'))),
        'orgFilters': list(map(org_map, data.get('QRY_LSTORGSHORT_DD_REF'))),
    }
