from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.bureau_exception_list as services
from talentmap_api.common.permissions import isDjangoGroupMember


class FSBidBureauExceptionsUsersView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Gets Bureau Exception List of Users
        '''
        result = services.get_bureau_exception_list(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauExceptionsBureausView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get Bureau Exception List of Bureaus
        '''
        result = services.get_users_bureau_list(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauExceptionsAddActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description='id'),
            'bureauCodeList': openapi.Schema(type=openapi.TYPE_STRING, description='bureauCodeList'),
        }
    ))

    def post(self, request):
        '''
        Adds Bureau from users Bureau Access List
        '''
        result = services.add_bureau_exception_list(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBureauExceptionsUpdateActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description='id'),
            'pvId': openapi.Schema(type=openapi.TYPE_STRING, description='pvId'),
            'bureauCodeList': openapi.Schema(type=openapi.TYPE_STRING, description='bureauCodes'),
            'lastUpdatedUserID': openapi.Schema(type=openapi.TYPE_STRING, description='lastUpdatedUserID'),
            'lastUpdated': openapi.Schema(type=openapi.TYPE_STRING, description='lastUpdated'),
        }
    ))

    def post(self, request):
        '''
        Updates Bureau from users Bureau Access List
        '''
        results = services.update_bureau_exception_list(request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBureauExceptionsDeleteActionView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description='id'),
            'pvId': openapi.Schema(type=openapi.TYPE_STRING, description='pvId'),
            'bureauCodeList': openapi.Schema(type=openapi.TYPE_STRING, description='bureauCodes'),
            'lastUpdatedUserID': openapi.Schema(type=openapi.TYPE_STRING, description='lastUpdatedUserID'),
            'lastUpdated': openapi.Schema(type=openapi.TYPE_STRING, description='lastUpdated'),
        }
    ))

    def post(self, request):
        '''
        Removes Bureau from users Bureau Access List
        '''
        results = services.delete_bureau_exception_list(request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
