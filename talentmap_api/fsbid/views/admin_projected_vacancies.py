import logging
import coreapi

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.admin_projected_vacancies as services

logger = logging.getLogger(__name__)

class FSBidAdminProjectedVacancyFiltersView(APIView):

    # ======================== Get PV Filters ========================

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets Filters for Admin Projected Vacancies
        '''
        result = services.get_admin_projected_vacancy_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyLanguageOffsetsView(APIView):

    # ======================== Get Language Offsets Dropdowns ========================

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets Language Offsets for Admin Projected Vacancies
        '''
        result = services.get_admin_projected_vacancy_language_offsets(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyListView(APIView):

    # ======================== Get PV List ========================

    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("bureaus", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureaus'),
            openapi.Parameter("organizations", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Organizations'),
            openapi.Parameter("bid_seasons", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Seasons'),
            openapi.Parameter("grades", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grades'),
            openapi.Parameter("skills", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skills'),
            openapi.Parameter("languages", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Languages'),
        ]
    )

    def get(self, request):
        '''
        Gets List Data for Admin Projected Vacancies 
        '''
        result = services.get_admin_projected_vacancies(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)