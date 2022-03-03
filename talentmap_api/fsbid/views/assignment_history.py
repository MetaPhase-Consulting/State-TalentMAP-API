import coreapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.assignment_history as services
from talentmap_api.common.permissions import isDjangoGroupMember

import logging
logger = logging.getLogger(__name__)


class FSBidAssignmentHistoryListView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("perdet", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Perdet of the employee'),
        ])

    def get(self, request, pk):
        '''
        Gets a single client's assignment history
        '''
        print('-------in assgin hist view--------')
        print('pk', pk)
        print('-------in assign hist view--------')
        return Response(services.create_ai_assignment_history(request.META['HTTP_JWT'], pk))
