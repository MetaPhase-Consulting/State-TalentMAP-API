import logging

from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.common.common_helpers import in_group_or_403

import talentmap_api.fsbid.services.bureau_exception_list as services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidBureauExceptionListView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get Bureau Exception List
        '''
        result = services.get_bureau_exception_list(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauExceptionBureauListView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('ao_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get Bureau Exception List Bureaus
        '''
        result = services.get_bureau_exception_list_of_bureaus(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidSaveBureauExceptionListActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='name'),
            'bureaus': openapi.Schema(type=openapi.TYPE_INTEGER, description='bureaus'),
        }
    ))

    def post(self, request):
        '''
        Add Bureau Exception List
        '''
        result = services.add_bureau_exception_list(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FSBidBureauExceptionUpdateView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='name'),
            'bureaus': openapi.Schema(type=openapi.TYPE_INTEGER, description='bureaus'),
        }
    ))

    def put(self, request, pk):
        '''
        Updates the selected bureau ID from bureau list
        '''
        user = UserProfile.objects.get(user=self.request.user)
        in_group_or_403(self.request.user, "superuser")

        results = services.update_bureau_exception_list(pk, request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBureauExceptionDeleteView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='name'),
            'bureaus': openapi.Schema(type=openapi.TYPE_INTEGER, description='bureaus'),
        }
    ))

    def delete(self, request, pk):
        '''
        Removes the selected bureau ID from bureau list
        '''
        results = services.delete_bureau_exception_list(pk, request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
