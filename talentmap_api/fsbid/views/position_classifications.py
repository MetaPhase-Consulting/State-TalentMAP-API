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

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.position_classifications as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidPositionClassificationsView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Position Classifications
        '''
        result = services.get_position_classifications(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPositionClassificationsActionView(APIView):

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position ID'),
            'updater_ids': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updater User IDs'),
            'updated_dates': openapi.Schema(type=openapi.TYPE_STRING, description='Updated Dates'),
            'codes': openapi.Schema(type=openapi.TYPE_STRING, description='Classification Codes'),
            'values': openapi.Schema(type=openapi.TYPE_STRING, description='Classification Values'),
        }
    ))

    def put(self, request):
        '''
        Edit Position Classifications
        '''
        result = services.edit_position_classifications(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
