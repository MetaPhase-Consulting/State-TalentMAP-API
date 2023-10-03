import logging

from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
import talentmap_api.fsbid.services.post_access as services

logger = logging.getLogger(__name__)

class FSBidPostAccessFiltersView(BaseView):
    '''
    Gets the Filters for the Post Access Pages
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_post_access_filters(jwt)
        return Response(result)

class FSBidPostAccessListView(BaseView):
    '''
    Gets the Data for the Post Access Pages
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_post_access_data(jwt, request.query_params)
        return Response(result)

class FSBidPostAccessActionView(BaseView):
    '''
    Updates Permissions for the Post Access Pages
    '''
    def delete(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.remove_post_access_permissions(jwt, request.data)
        return Response(result)
    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.grant_post_access_permissions(jwt, request.data)
        return Response(result)
