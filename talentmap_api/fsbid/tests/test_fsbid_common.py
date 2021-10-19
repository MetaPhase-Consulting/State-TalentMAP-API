import pytest
import datetime
from talentmap_api.fsbid.services.common import sort_bids


def test_sort_bids():
    mock_bids = [
        { 'id': 1, 'status': 'declined', 'create_date': datetime.datetime(2022, 5, 17), 'position_info': { 'position': { 'post': { 'location': { 'city': 'Alpharetta' } } } } },
        { 'id': 2, 'status': 'closed', 'create_date': datetime.datetime(2022, 5, 12), 'position_info': { 'position': { 'post': { 'location': { 'city': 'Denver' } } } } },
        { 'id': 3, 'status': 'handshake_offered', 'create_date': datetime.datetime(2022, 5, 20), 'position_info': { 'position': { 'post': { 'location': { 'city': 'Washington' } } } } },
        { 'id': 4, 'status': 'in_panel', 'create_date': datetime.datetime(2022, 5, 11), 'position_info': { 'position': { 'post': { 'location': { 'city': 'Bethesda' } } } } },
        { 'id': 5, 'status': 'submitted', 'create_date': datetime.datetime(2022, 5, 14), 'position_info': { 'position': { 'post': { 'location': { 'city': None } } } },
     }]

    bids = sort_bids(mock_bids, 'status')
    assert bids[0]['id'] == 4
    assert bids[1]['id'] == 3
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 2
    assert bids[4]['id'] == 1

    bids = sort_bids(mock_bids, '-status')
    assert bids[0]['id'] == 1
    assert bids[1]['id'] == 2
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 3
    assert bids[4]['id'] == 4

    bids = sort_bids(mock_bids, 'bidlist_create_date')
    assert bids[0]['id'] == 4
    assert bids[1]['id'] == 2
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 1
    assert bids[4]['id'] == 3

    bids = sort_bids(mock_bids, 'bidlist_location')
    assert bids[0]['id'] == 5 # empty strings come first
    assert bids[1]['id'] == 1
    assert bids[2]['id'] == 4
    assert bids[3]['id'] == 2
    assert bids[4]['id'] == 3