import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.admin_projected_vacancies as services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidAdminProjectedVacancyFiltersView(BaseView):

    # ======================== Get PV Filters ========================

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets admin projected vacancy filters
        '''
        result = services.get_admin_projected_vacancy_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyListView(BaseView):

    # ======================== Get PV List ========================

    permission_classes = (IsAuthenticatedOrReadOnly,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'bureaus': openapi.Schema(type=openapi.TYPE_STRING, description='bureaus'),
            'organizations': openapi.Schema(type=openapi.TYPE_STRING, description='organizations'),
            'bidSeasons': openapi.Schema(type=openapi.TYPE_STRING, description='bid_seasons'),
            'grades': openapi.Schema(type=openapi.TYPE_STRING, description='grades'),
            'skills': openapi.Schema(type=openapi.TYPE_STRING, description='skills'),
            'languages': openapi.Schema(type=openapi.TYPE_STRING, description='languages'),
        }
    ))

    def get(self, request):
        '''
        Gets admin projected vacancies
        '''
        result = services.get_admin_projected_vacancies(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyLanguageOffsetsView(BaseView):

    # ======================== Get Language Offsets Dropdowns ========================

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets admin projected vacancy language offsets
        '''
        result = services.get_admin_projected_vacancy_language_offsets(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)
