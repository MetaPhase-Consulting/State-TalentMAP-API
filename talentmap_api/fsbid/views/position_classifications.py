import logging
import coreapi

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.position_classifications as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidPositionClassificationsView(APIView):
    # perms TBD
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets Position Classifications
        '''
        result = services.get_position_classifications(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPositionClassificationsActionView(APIView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='pos_seq_num'),
            'updater_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='updater_id'),
            'position_classifications': openapi.Schema(type=openapi.TYPE_STRING, description='position_classifications'),
        }
    ))

    def post(self, request):
        '''
        Edit Position Classifications
        '''
        result = services.edit_position_classifications(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)