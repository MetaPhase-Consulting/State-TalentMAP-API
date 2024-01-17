from rest_condition import Or
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.org_stats as services
from talentmap_api.common.permissions import isDjangoGroupMember
from django.core.exceptions import ValidationError


class FSBidOrgStatsView(APIView):
    print("APPPPPPPLEEEESSSS")
    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Get All 
        '''
        result = services.get_org_stats(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
