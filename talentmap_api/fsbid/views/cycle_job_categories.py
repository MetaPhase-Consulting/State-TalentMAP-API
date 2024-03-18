import logging
import coreapi

from rest_condition import Or
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.cycle_job_categories as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidCycleCategoriesView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Cycle Categories
        '''
        result = services.get_cycle_categories(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
    
class FSBidCycleJobCategoriesView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Cycle Job Categories
        '''
        result = services.get_cycle_job_categories(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidCycleJobCategoriesActionView(APIView):

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'included': openapi.Schema(type=openapi.TYPE_INTEGER, description='Inclusion Indicators'),
            'cycle_codes': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Category Code'),
            'job_codes': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Job Category Codes'),
            'updater_ids': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updater User IDs'),
            'updated_dates': openapi.Schema(type=openapi.TYPE_STRING, description='Updated Dates'),
        }
    ))

    def put(self, request):
        '''
        Edit Cycle Job Categories
        '''
        result = services.edit_cycle_job_categories(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
