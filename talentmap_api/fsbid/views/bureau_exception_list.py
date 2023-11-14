from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.bureau_exceptions as services
from talentmap_api.common.permissions import isDjangoGroupMember


class FSBidBureauExceptionsView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get Bureau Exceptions
        '''
        result = services.get_bureau_exceptions(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauExceptionsUserMetaDataView(APIView):
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get User Bureau Exceptions and MetaData Required for Actions
        '''
        result = services.get_user_bureau_exceptions_and_metadata(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauExceptionsUserAddActionView(APIView):
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
        Add Bureau Exceptions to a User
        used the first time Bureau Exceptions are added to a user
        '''
        result = services.add_user_bureau_exceptions(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBureauExceptionsUserUpdateActionView(APIView):
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
        Update User Bureau Exceptions
        '''
        results = services.update_user_bureau_exceptions(request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBureauExceptionsUserDeleteActionView(APIView):
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
        Deletes all Bureau Exceptions from a User
        will remove all Bureau Exceptions from User, regardless of it all Bureaus are sent in for removal
        '''
        results = services.delete_user_bureau_exceptions(request.data, request.META['HTTP_JWT'])
        if results is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
