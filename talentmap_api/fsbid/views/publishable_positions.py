import logging

from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.publishable_positions as services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidPublishablePositionsView(APIView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), ) ]

    def get(self, request, pk):
        '''
        Get Publishable Positions
        '''
        result = services.get_publishable_positions(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPublishablePositionsFiltersView(BaseView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), )]

    def get(self, request, *args, **kwargs):
        '''
        Get Publishable Positions Filters
        '''
        print('🌷🌷🌷🌷🌷🌷🌷🌷🌷')
        print('in filters view')
        print('🌷🌷🌷🌷🌷🌷🌷🌷🌷')
        result = services.get_publishable_positions_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidPublishablePositionsActionView(APIView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='pos_seq_num'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='capsule_descr_txt'),
            'updater_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='update_id'),
        }
    ))

    def patch(self, request, pk):
        '''
        Edit Publishable Position
        '''
        try:
            services.edit_publishable_position(request.META['HTTP_JWT'], pk, **request.data)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
