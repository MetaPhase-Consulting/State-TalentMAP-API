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
import talentmap_api.fsbid.services.notifications as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidNoteCableView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('I_ASG_SEQ_NUM', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Asg Seq Num'),
        openapi.Parameter('I_ASGD_REVISION_NUM', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Asg Revision Num'),
    ])

    def get(self, request):
        '''
        Gets Note Cable
        '''
        result = services.get_note_cable(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidCableView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('I_NM_SEQ_NUM', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='NM Seq Num'),
        openapi.Parameter('I_NM_NOTIFICATION_IND', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='NM Notification Indicator'),
    ])

    def get(self, request):
        '''
        Gets Cable
        '''
        result = services.get_cable(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidNoteCableReferenceView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('I_NM_SEQ_NUM', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='NM Seq Num'),
    ])

    def get(self, request):
        '''
        Gets Note Cable Reference
        '''
        result = services.get_note_cable_ref(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidNoteCableEditView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'I_HDR_NME_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='Note ID'),
            'I_HDR_CLOB_LENGTH': openapi.Schema(type=openapi.TYPE_INTEGER, description='Clob Length'),
            'I_HDR_NME_OVERRIDE_CLOB': openapi.Schema(type=openapi.TYPE_INTEGER, description='Override Values'),
            'I_HDR_NME_UPDATE_ID': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updater ID'),
            'I_HDR_NME_UPDATE_DATE': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updated Date'),
            'I_HDR_NME_CLEAR_IND': openapi.Schema(type=openapi.TYPE_INTEGER, description='Clear Indicator'),
        }
    ))

    def post(self, request):
        '''
        Edits Note Cable
        '''
        result = services.edit_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class FSBidNoteCableRebuildView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'I_NM_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='Note ID'),
            'I_NME_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='Note ID'),
            'I_NME_UPDATE_ID': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updater ID'),
            'I_NME_UPDATE_DATE': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updated Date'),
        }
    ))

    def put(self, request):
        '''
        Rebuilds Note Cable (Whole/Tab)
        '''
        result = services.rebuild_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class FSBidNoteCableStoreView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'I_NM_SEQ_NUM': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Store Note Cable (PDF in EOPF)
        '''
        result = services.store_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidNoteCableSendView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_NM_SEQ_NUM_I': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Sends Note Cable (Update Sent Date)
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidGetOpsWsdlView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    def get(self, request):
        '''
        Get OPS WSDL
        '''
        result = services.get_ops_wsdl(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidGetOpsDataView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('PV_NM_SEQ_NUM_I', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Note ID'),
    ])

    def get(self, request):
        '''
        Get OPS Data
        '''
        result = services.get_ops_data(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidCreateOpsLogView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_OTL_TM_DATA_I': openapi.Schema(type=openapi.TYPE_STRING, description='SOAP Message (XML)'),
            'PV_ETL_SEQ_NBR_I': openapi.Schema(type=openapi.TYPE_STRING, description='ETL ID'),
        }
    ))

    def put(self, request):
        '''
        Create OPS Log
        '''
        result = services.create_ops_log(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidUpdateOpsLogView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_OTL_ID_I': openapi.Schema(type=openapi.TYPE_STRING, description='Log ID'),
            'PV_OTL_SUBMIT_RETURN_CODE_I': openapi.Schema(type=openapi.TYPE_STRING, description='Return Code'),
            'PV_OTL_SUBMIT_MESSAGE_I': openapi.Schema(type=openapi.TYPE_STRING, description='Return Message'),
        }
    ))

    def post(self, request):
        '''
        Update OPS Log
        '''
        result = services.update_ops_log(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBIDGalLookupView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('PV_LAST_NAME_I', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Last Name'),
    ])

    def get(self, request):
        '''
        GAL Lookup
        '''
        result = services.gal_lookup(request.query_params, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)