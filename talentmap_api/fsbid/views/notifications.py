import logging
import coreapi
# import secure_smtplib
import os

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
        Store Note Cable
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
        Sends Note Cable
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidGetOpsView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_NM_SEQ_NUM_I': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Sends Note Cable
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidListOpsView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_NM_SEQ_NUM_I': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Sends Note Cable
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidInsertOpsView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_NM_SEQ_NUM_I': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Sends Note Cable
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidUpdateOpsView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'PV_NM_SEQ_NUM_I': openapi.Schema(type=openapi.TYPE_STRING, description='Note ID'),
        }
    ))

    def post(self, request):
        '''
        Sends Note Cable
        '''
        result = services.send_note_cable(request.data, request.META['HTTP_JWT'])
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
    

class GetEmailFromRequest(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    def get(self, request):
        logger.info("Inside GetLoggedInEmail view")
        logger.info("request.META: ", request.META, "\n")
        if request.user.is_authenticated:
            email = request.user.email
            # this is for Dev1 testing, all logged in user have a @dosdev.us email,
            # this needs to be changed to @state.gov - all usernames are the same for 
            # dosdev and state.gov
            print("email: ", email, "\n")
            if email.endswith("@dosdev.us"):
                email = email.replace("@dosdev.us", "@state.gov")
            return Response({'email': email})
        else:
            return Response({'email': 'Not logged in'})
        
        
class SendSMTPEmailViewOne(APIView):
    """
    This endpoint is meant to test getting the envrironment variables 
    that are required to test sending an email using the SMTP server.

    For testing in Dev1, the from email will be talentmap@elguaria.net,
    otherwise it will be the email of the logged in user.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, Or(isDjangoGroupMember('superuser'), isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'to': openapi.Schema(type=openapi.TYPE_STRING, description='To email'),
            'subject': openapi.Schema(type=openapi.TYPE_STRING, description='Subject'),
            'body': openapi.Schema(type=openapi.TYPE_STRING, description='Body'),
        }
    ))

    def post(self, request):
        # SMTP Server configuration:
        host = os.getenv('EMAIL_HOST')
        port = os.getenv('EMAIL_PORT')
        from_email = os.getenv('EMAIL_FROM_ADDRESS')
        to = "shahm1@state.gov"
        subject = "Test Email V1"
        body = "This is a test email V1"
        footer = 'SBU - PRIVACY OR PII'

        print("request.user.email: ", GetEmailFromRequest(), "\n")
        print("host: ", host, "\n")
        print("port: ", port, "\n")
        print("from_email: ", from_email, "\n")
        print("to: ", to, "\n")
        print("subject: ", subject, "\n")
        print("body: ", body, "\n")
        print("footer: ", footer, "\n")


        return Response({
            'host': host,
            'port': port,
            'from_email': from_email,
            'to': to,
            'subject': subject,
            'body': body,
            'footer': footer
        })
    
    
class SendSMTPEmailViewTwo(APIView):
    def post(self, request):
        # SMTP Server configuration:
        host = os.getenv('SMTP_HOST')
        port = os.getenv('SMTP_PORT')
        from_email = os.getenv('SMTP_DEV1_EMAIL')
        to = ["imbrianofa@state.gov", "ShahM1@state.gov"]
        subject = "Test Email V2"
        body = "This is a test email V2"
        footer = os.getenv('SMTP_EMAIL_FOOTER')

        # sending the email with smtp:
        # secure_smtplib.send_email(host, port, from_email, to, subject, body, footer)