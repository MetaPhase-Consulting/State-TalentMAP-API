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

import talentmap_api.fsbid.services.bidding_tool as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

actions_properties = {
    'location': openapi.Schema(type=openapi.TYPE_STRING, description='GSA Location Code'),
    'snd': openapi.Schema(type=openapi.TYPE_STRING, description='Service Needs Diff'),
    'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status Code'),
    'hds': openapi.Schema(type=openapi.TYPE_STRING, description='Most Diff To Staff Flag'),
    'tod': openapi.Schema(type=openapi.TYPE_STRING, description='TOD Code'),
    'rr_point': openapi.Schema(type=openapi.TYPE_STRING, description='Rest and Relaxation Point Text'),
    'unaccompanied_status': openapi.Schema(type=openapi.TYPE_INTEGER, description='Unaccompanied Status Code'),
    'apo_fpo_dpo': openapi.Schema(type=openapi.TYPE_STRING, description='APO or FPO Flag'),
    'cola': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cost of Living'),
    'differential_rate': openapi.Schema(type=openapi.TYPE_INTEGER, description='Differential Rate'),
    'danger_pay': openapi.Schema(type=openapi.TYPE_INTEGER, description='Danger Pay'),
    'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='Remarks Text'),
    'climate_zone': openapi.Schema(type=openapi.TYPE_INTEGER, description='Climate Zone'),
    'housing': openapi.Schema(type=openapi.TYPE_STRING, description='Housing Type Code'),
    'quarters': openapi.Schema(type=openapi.TYPE_STRING, description='Quarters Type Code'),
    'consumable_allowance': openapi.Schema(type=openapi.TYPE_STRING, description='Consumable Allowance Flag'),
    'quarters_remark': openapi.Schema(type=openapi.TYPE_STRING, description='Quarters Remark Text'),
    'special_ship_allowance': openapi.Schema(type=openapi.TYPE_STRING, description='Special Ship Allowance Text'),
    'fm_fp': openapi.Schema(type=openapi.TYPE_STRING, description='Foreign Made Prov Flag'),
    'school_year': openapi.Schema(type=openapi.TYPE_STRING, description='School Year Text'),
    'grade_education': openapi.Schema(type=openapi.TYPE_STRING, description='Grate Education Text'),
    'efm_employment': openapi.Schema(type=openapi.TYPE_STRING, description='EFM Employment Text'),
    'inside_efm_employment': openapi.Schema(type=openapi.TYPE_STRING, description='Inside EFM Employement Flag'),
    'outside_efm_employment': openapi.Schema(type=openapi.TYPE_STRING, description='Outside EFM Employement Flag'),
    'efm_issues': openapi.Schema(type=openapi.TYPE_STRING, description='EFM Issue Code'),
    'medical': openapi.Schema(type=openapi.TYPE_STRING, description='Medical Remarks Text'),
}

class FSBidBiddingToolView(APIView):

    # ======================== Get Bidding Tool ========================

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, pk):
        '''
        Gets Bidding Tool
        '''
        result = services.get_bidding_tool(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
    

class FSBidBiddingToolActionsView(APIView):

    # ======================== Get Bidding Tool List ========================

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        '''
        Gets list of all Bidding Tool
        '''
        result = services.get_bidding_tools(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


    # ======================== Delete Bidding Tool ========================

    permission_classes = [IsAuthenticated, isDjangoGroupMember('superuser'), ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("location", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='GSA Location Code'),
            openapi.Parameter("updater_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Updater User ID'),
            openapi.Parameter("updated_date", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Updated Date'),
        ])

    def delete(self, request):
        '''
        Deletes Bidding Tool
        '''
        result = services.delete_bidding_tool(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


    # ======================== Create Bidding Tool ========================

    permission_classes = [IsAuthenticated, isDjangoGroupMember('superuser'), ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=actions_properties
    ))
    
    def post(self, request):
        '''
        Create Bidding Tool
        '''
        result = services.create_bidding_tool(request.data, request.META['HTTP_JWT'])
        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for creating Bidding Tool failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(result)
    
    
    # ======================== Edit Bidding Tool ========================

    permission_classes = [IsAuthenticated, isDjangoGroupMember('superuser'), ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            **actions_properties,
            'updater_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updater User ID'),
            'updated_date': openapi.Schema(type=openapi.TYPE_STRING, description='Updated Date'),
        }
    ))

    def put(self, request):
        '''
        Edit Bidding Tool
        '''
        result = services.edit_bidding_tool(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidBiddingToolCreateView(APIView):

    # ======================== Get Bidding Tool Create Data ========================

    permission_classes = [IsAuthenticated, isDjangoGroupMember('superuser'), ]

    def get(self, request):
        '''
        Gets Bidding Tool Create Data
        '''
        result = services.get_bidding_tool_create_data(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)