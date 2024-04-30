import logging
import coreapi

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_condition import Or
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.user_profile.models import UserProfile
import talentmap_api.fsbid.services.assignment_history as services

logger = logging.getLogger(__name__)


# ======== Assignment History ========

class FSBidAssignmentHistoryListView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.')
        ])

    def get(self, request, pk):
        '''
        Gets a single client's assignment history
        '''
        query_copy = request.query_params.copy()
        query_copy["perdet_seq_num"] = pk
        query_copy["ordering"] = "-assignment_start_date"
        query_copy._mutable = False
        data = services.assignment_history_to_client_format(services.get_assignments(query_copy, request.META['HTTP_JWT']))
        return Response(data)

class FSBidPrivateAssignmentHistoryListView(BaseView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.')
        ])

    def get(self, request):
        '''
        Gets current users assignment history
        '''
        try:
            user = UserProfile.objects.get(user=self.request.user)
            query_copy = request.query_params.copy()
            query_copy["perdet_seq_num"] = user.emp_id
            query_copy["ordering"] = "-assignment_start_date"
            query_copy._mutable = False
            data = services.assignment_history_to_client_format(services.get_assignments(query_copy, request.META['HTTP_JWT']))
            return Response(data)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# ======== Maintain Assignments/Separations ========

class FSBidMaintainAssignmentsSeparationsListView(APIView):
    def get(self, request, pk):
        '''
        Get Maintain Assignments and Separations List
        '''
        return Response(services.get_assignments_separations(pk, request.META['HTTP_JWT']))

# ======== Maintain Assignments ========

class FSBidMaintainAssignmentsBaseView(APIView):
    def post(self, request):
        '''
        Create Assignment
        '''
        return Response(services.create_assignment_separation(request.data, request.META['HTTP_JWT'], 0))

class FSBidMaintainAssignmentsActionView(BaseView):
    def get(self, request, pk, id):
        '''
        Get Assignment Detail and Reference Data
        '''
        query = { 
            "perdet_seq_num": pk,
            "asg_id": id,
            "revision_num": request.query_params.get("revision_num"),
        }
        return Response(services.get_assignment_separation_detail(query, request.META['HTTP_JWT'], 0))
    def patch(self, request):
        '''
        Update Assignment
        '''
        return Response(services.update_assignment_separation(request.data, request.META['HTTP_JWT'], 0))
    

# ======== Maintain Separations ========

class FSBidmaintainSeparationsListBaseView(APIView):
    def post(self, request):
        '''
        Create Separation
        '''
        return Response(services.create_assignment_separation(request.data, request.META['HTTP_JWT'], 1))
    
class FSBidmaintainSeparationsListActionView(BaseView):
    def get(self, request, pk, id):
        '''
        Get Separation Detail and Reference Data
        '''
        query = { 
            "perdet_seq_num": pk,
            "sep_id": id,
            "revision_num": request.query_params.get("revision_num"),
        }
        return Response(services.get_assignment_separation_detail(query, request.META['HTTP_JWT'], 1))
    def patch(self, request):
        '''
        Update Separation
        '''
        return Response(services.update_assignment_separation(request.data, request.META['HTTP_JWT'], 1))
