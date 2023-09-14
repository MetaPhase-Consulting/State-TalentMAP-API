import logging

from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
import talentmap_api.fsbid.services.manage_bid_seasons as services

logger = logging.getLogger(__name__)

class FSBidManageBidSeasonsView(BaseView):
    '''
    Gets the Data for the Manage Bid Seasons Page
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_bid_seasons_data(jwt, request.query_params)
        return Response(result)
    '''
    Edit an existing Bid Season
    '''
    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_bid_seasons_data(jwt, request.data)
        return Response(result)
