import logging
import pydash

from talentmap_api.bidding.models import BidHandshake
from talentmap_api.common.common_helpers import ensure_date

logger = logging.getLogger(__name__)


def get_position_handshake_data(cp_id):
    '''
    Return whether the cycle position is active and to which perdet, if any, possesses the active handshake
    '''
    props = {
        'active': False,
        'active_handshake_perdet': None,
    }

    hs = BidHandshake.objects.filter(cp_id=cp_id).values()
    active = pydash.filter_(hs, lambda x: x['status'] is not 'R')
    if len(active) is 0:
        props['active'] = True
    
    active = pydash.find(hs, lambda x: x['status'] is 'O' or x['status'] is 'A')
    if active:
        props['active_handshake_perdet'] = active['bidder_perdet']

    return props


def get_bidder_handshake_data(cp_id, perdet):
    '''
    Return handshake data for a given perdet and cp_id
    '''
    mapping = {
        'O': "handshake_offered",
        'A': "handshake_offered", # can assume 'offered', otherwise bidder could not have accepted
        'D': "handshake_offered", # can assume 'offered', otherwise bidder could not have declined
        'R': "handshake_revoked",
    }

    bidder_mapping = {
        'A': "handshake_accepted",
        'D': "handshake_declined",
    }

    props = {
        'hs_status_code': None,
        'bidder_hs_code': None,
        'hs_cdo_indicator': False,
        'hs_date_accepted': None,
        'hs_date_declined': None,
        'hs_date_offered': None,
        'hs_date_revoked': None,
    }

    hs = BidHandshake.objects.filter(cp_id=cp_id, bidder_perdet=perdet)

    if hs.exists():
        hs = hs.first()
        status = hs.status
        bidder_status = hs.bidder_status
        is_cdo_update = hs.is_cdo_update == 1

        props['hs_status_code'] = mapping[status]
        props['hs_cdo_indicator'] = is_cdo_update

        if bidder_status is 'D':
            props['bidder_hs_code'] = bidder_mapping['D']

        if bidder_status is 'A':
            props['bidder_hs_code'] = bidder_mapping['A']

        # Dates
        props['hs_date_accepted'] = ensure_date(hs.date_accepted)
        props['hs_date_declined'] = ensure_date(hs.date_declined)
        props['hs_date_offered'] = ensure_date(hs.date_offered)
        props['hs_date_revoked'] = ensure_date(hs.date_revoked)

    return props