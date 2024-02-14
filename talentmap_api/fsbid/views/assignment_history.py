import logging
import coreapi

from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.fsbid.services.assignment_history import alt_update_assignment, alt_create_assignment, alt_get_assignments, get_assignments, assignment_history_to_client_format, get_assignment_ref_data
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


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
        data = assignment_history_to_client_format(get_assignments(query_copy, request.META['HTTP_JWT']))
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
            data = assignment_history_to_client_format(get_assignments(query_copy, request.META['HTTP_JWT']))
            return Response(data)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FSBidAssignmentReferenceView(BaseView):
    def get(self, request, pk, asg_id):
        '''
        Get ref data for maintain assignment
        '''
        query = { 
            "perdet_seq_num": pk,
            "asg_id": asg_id,
            "revision_num": request.query_params.get("revision_num"),
        }
        return Response(get_assignment_ref_data(query, request.META['HTTP_JWT']))

class FSBidAltAssignmentHistoryListView(BaseView):
    def get(self, request, pk):
        '''
        Fetch asg sep history by perdet from fsbid proc
        '''
        return Response(alt_get_assignments(pk, request.META['HTTP_JWT']))

    def patch(self, request, pk):
        '''
        Update existing asg sep by perdet from fsbid proc
        '''
        return Response(alt_update_assignment(request.data, request.META['HTTP_JWT']))


    def post(self, request, pk):
        '''
        Create asg sep by perdet from fsbid proc
        '''
        return Response(alt_create_assignment(request, request.META['HTTP_JWT']))


