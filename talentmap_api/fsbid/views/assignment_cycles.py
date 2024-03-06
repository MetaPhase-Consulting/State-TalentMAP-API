import logging

from rest_condition import Or
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.assignment_cycles as services

from talentmap_api.common.permissions import isDjangoGroupMember

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
        return Response(result)


class FSBidAssignmentCycleListView(BaseView):
    '''
    Gets the Data for single Assignment Cycle
    '''

    def post(self, request, pk):
        jwt = request.META['HTTP_JWT']
        result = services.get_assignment_cycle_data(jwt, pk)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidAssignmentCyclesUpdateView(BaseView):
    '''
    Update an Assignment Cycle for the Cycle Management Page
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_assignment_cycle(jwt, request.data)
        return Response(result)


class FSBidAssignmentCyclesPostPosView(BaseView):
    '''
    Post Open Positions for an Assignment Cycle
    '''

    def post(self, request, pk):
        jwt = request.META['HTTP_JWT']
        result = services.post_assignment_cycle_positions(jwt, pk)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidAssignmentCyclesDeleteView(BaseView):
    '''
    Delete an Assignment Cycle
    '''

    def post(self, request, pk):
        jwt = request.META['HTTP_JWT']
        result = services.delete_assignment_cycle(jwt, pk)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidCyclePositionsFiltersView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), )]

    def get(self, request, *args, **kwargs):
        '''
        Get Cycle Positions Filters
        '''
        jwt = request.META['HTTP_JWT']
        result = services.get_cycle_positions_filters(jwt)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidCyclePositionsView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), )]

    def post(self, request, *args, **kwargs):
        '''
        Get Cycle Positions
        '''
        jwt = request.META['HTTP_JWT']
        result = services.get_cycle_positions(jwt, request.data)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
