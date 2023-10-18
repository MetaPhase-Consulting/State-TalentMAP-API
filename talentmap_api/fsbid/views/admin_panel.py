import logging

from rest_condition import Or
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.admin_panel as services
from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.common.common_helpers import view_result


logger = logging.getLogger(__name__)


# ======================== Panel Remark ========================

class CreateRemarkView(BaseView):

    def post(self, request):
        '''
        Saves a new Remark
        '''
        try:
            services.submit_create_remark(request.data, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# ======================== Panel Meeting ========================

class FSBidPanelMeetingView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Panel Meeting
        '''
        result = services.get_panel_meeting(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

# ======================== Edit Panel Meeting ========================

class FSBidPanelMeetingActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('cdo_user'), isDjangoGroupMember('superuser'), isDjangoGroupMember('ao_user')) ]

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
        Edit Panel Meeting
        '''
        result = services.edit_panel_meeting(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
# ======================== Post Panel Processing ========================

class FSBidPostPanelView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Post Panel Processing
        '''
        result = services.get_post_panel(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
    
# ======================== Edit Post Panel Processing ========================

class FSBidPostPanelActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('cdo_user'), isDjangoGroupMember('superuser'), isDjangoGroupMember('ao_user')) ]

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
        Edit Post Panel Processing
        '''
        result = services.edit_post_panel(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
# ======================== Panel Run Actions ========================

class FSBidRunPreliminaryActionView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('cdo_user'), isDjangoGroupMember('superuser'), isDjangoGroupMember('ao_user')) ]

    def put(self, request, pk):
        '''
        Run Panel Official Preliminary
        '''
        result = services.run_preliminary(pk, request.META['HTTP_JWT'])
        return view_result(result)
    
class FSBidRunAddendumActionView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('cdo_user'), isDjangoGroupMember('superuser'), isDjangoGroupMember('ao_user')) ]

    def put(self, request, pk):
        '''
        Run Panel Official Addendum
        '''
        result = services.run_addendum(pk, request.META['HTTP_JWT'])
        return view_result(result)
    
class FSBidRunPostPanelActionView(BaseView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('cdo_user'), isDjangoGroupMember('superuser'), isDjangoGroupMember('ao_user')) ]

    def put(self, request, pk):
        '''
        Run Post Panel
        '''
        result = services.run_post_panel(pk, request.META['HTTP_JWT'])
        return view_result(result)