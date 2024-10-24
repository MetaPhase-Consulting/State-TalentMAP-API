import logging

from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError

import talentmap_api.fsbid.services.publishable_positions as services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidPublishablePositionsView(APIView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('post_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get Publishable Positions
        '''
        result = services.get_publishable_positions(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPublishablePositionsActionView(APIView):
    # perms TBD
    # Todo: split up the edit action across the different roles to separate the permissions to edit each field
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('post_user'), isDjangoGroupMember('superuser'), )]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'posSeqNum': openapi.Schema(type=openapi.TYPE_INTEGER, description='pos_seq_num'),
            'psCD': openapi.Schema(type=openapi.TYPE_STRING, description='ps_cd'),
            'aptSeqNum': openapi.Schema(type=openapi.TYPE_STRING, description='apt_seq_num'),
            'created': openapi.Schema(type=openapi.TYPE_STRING, description='create_date'),
            'createdUserID': openapi.Schema(type=openapi.TYPE_STRING, description='create_id'),
            'positionDetailsLastUpdated': openapi.Schema(type=openapi.TYPE_STRING, description='capsule_desc_update_date'),
            'posAuditExclusionInd': openapi.Schema(type=openapi.TYPE_STRING, description='exclusion_ind'),
            'positionDetails': openapi.Schema(type=openapi.TYPE_STRING, description='capsule_descr_txt'),
            'lastUpdated': openapi.Schema(type=openapi.TYPE_INTEGER, description='update_date'),
            'lastUpdatedUserID': openapi.Schema(type=openapi.TYPE_INTEGER, description='update_id'),
        }
    ))

    def post(self, request):
        '''
        Edit Publishable Position
        '''
        try:
            services.edit_publishable_position(request.data, request.META['HTTP_JWT'])
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidPublishablePositionsFiltersView(BaseView):
    # perms TBD
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('post_user'), isDjangoGroupMember('superuser'), )]

    def get(self, request, *args, **kwargs):
        '''
        Get Publishable Positions Filters
        '''
        result = services.get_publishable_positions_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPublishablePositionsCSVView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('post_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Exports Publishable Positions to CSV format
        '''
        return services.get_publishable_positions_csv(request.query_params, request.META['HTTP_JWT'])

