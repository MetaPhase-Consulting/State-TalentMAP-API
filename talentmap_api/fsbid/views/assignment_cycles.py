import logging

from rest_framework import status
from rest_framework.response import Response
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.assignment_cycles as services

logger = logging.getLogger(__name__)


class FSBidAssignmentCyclesListView(BaseView):
    '''
    Gets the Data for the Assignment Cycle Management Page
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_assignment_cycles_data(jwt, request.query_params)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidAssignmentCyclesCreateView(BaseView):
    '''
    Create a new Assignment Cycle for the Cycle Management Page
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.create_assignment_cycle(jwt, request.data)
        return result
