import logging

from rest_condition import Or
from rest_framework import status
from rest_framework.views import APIView
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

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Assignment Cycles failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCyclesCreateView(APIView):
    '''
    Create a new Assignment Cycle for the Cycle Management Page
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.create_assignment_cycle(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Creating Assignment Cycle failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCycleListView(BaseView):
    '''
    Gets the Data for single Assignment Cycle
    '''

    def get(self, request, pk):
        jwt = request.META['HTTP_JWT']
        result = services.get_assignment_cycle_data(jwt, pk)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Get Assignment Cycle failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCyclesUpdateView(APIView):
    '''
    Update an Assignment Cycle for the Cycle Management Page
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_assignment_cycle(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update Assignment Cycle failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCyclesPostPosView(BaseView):
    '''
    Post Open Positions for an Assignment Cycle
    '''

    def get(self, request, pk):
        jwt = request.META['HTTP_JWT']
        result = services.post_assignment_cycle_positions(jwt, pk)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Post Open Positions failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCyclesDeleteView(APIView):
    '''
    Delete an Assignment Cycle
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.delete_assignment_cycle(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Delete Assignment Cycle failed")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAssignmentCyclesMergeView(APIView):
    '''
    Merge two Assignment Cycles
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.merge_assignment_cycles(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Merge Assignment Cycle failed")
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

    def get(self, request):
        '''
        Get Cycle Positions
        '''
        jwt = request.META['HTTP_JWT']
        result = services.get_cycle_positions(jwt, request.query_params)
        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Get Cycle Positions Failed")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidCyclePositionView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), )]

    def get(self, request, pk):
        '''
        Get Single Cycle Position - with more specific data
        '''
        jwt = request.META['HTTP_JWT']
        result = services.get_cycle_position(jwt, pk)
        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Get Cycle Position Failed")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidCyclePositionUpdateView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), )]
    '''
    Update a Cycle Position
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_cycle_position(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update Assignment Cycle Date Classifications Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidCycleClassificationsView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), )]
    # Bureau & AO can View, only Admin can Edit

    def get(self, request):
        '''
        Get Cycle Classifications
        '''
        jwt = request.META['HTTP_JWT']
        result = services.get_cycle_classifications(jwt, request.query_params)
        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Get Cycle Classifications Failed")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidCycleClassificationsUpdateView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('superuser'), )]
    '''
    Update an Assignment Cycle Date Classifications
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_assignment_cycles_classifications(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update Assignment Cycle Date Classifications Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
