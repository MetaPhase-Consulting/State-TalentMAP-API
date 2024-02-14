import logging
import coreapi

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.admin_projected_vacancies as services
from talentmap_api.common.permissions import isDjangoGroupMember

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
        result = services.get_admin_projected_vacancies(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyActionsView(APIView):
    
    # ======================== Edit PV ========================

    permission_classes = [IsAuthenticated, isDjangoGroupMember('superuser'), ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'future_vacancy_seq_num': openapi.Schema(type=openapi.TYPE_STRING, description='Projected Vacancy Seq Num'),
            'future_vacancy_seq_num_ref': openapi.Schema(type=openapi.TYPE_STRING, description='Projected Vacancy Seq Num Reference'),
            'positon_seq_num': openapi.Schema(type=openapi.TYPE_STRING, description='Position Seq Num'),
            'bid_season_code': openapi.Schema(type=openapi.TYPE_STRING, description='Bid Season Code'),
            'assignment_seq_num_effective': openapi.Schema(type=openapi.TYPE_STRING, description='Assignment Seq Num Effective'),
            'assignment_seq_num': openapi.Schema(type=openapi.TYPE_STRING, description='Assignment Seq Num'),
            'cycle_date_type_code': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Date Type Code'),
            'future_vacancy_status_code': openapi.Schema(type=openapi.TYPE_STRING, description='Status Code'),
            'future_vacancy_override_code': openapi.Schema(type=openapi.TYPE_STRING, description='Override Code'),
            'future_vacancy_override_tour_end_date': openapi.Schema(type=openapi.TYPE_STRING, description='Override TED'),
            'future_vacancy_system_indicator': openapi.Schema(type=openapi.TYPE_STRING, description='System Indicator'),
            'future_vacancy_comment': openapi.Schema(type=openapi.TYPE_STRING, description='Comment'),
            'created_date': openapi.Schema(type=openapi.TYPE_STRING, description='Created Date'),
            'creator_id': openapi.Schema(type=openapi.TYPE_STRING, description='Creator ID'),
            'updater_id': openapi.Schema(type=openapi.TYPE_STRING, description='Updater ID'),
            'updated_date': openapi.Schema(type=openapi.TYPE_STRING, description='Updated Date'),
            'future_vacancy_mc_indicator': openapi.Schema(type=openapi.TYPE_STRING, description='MC Indicator'),
            'future_vacancy_exclude_import_indicator': openapi.Schema(type=openapi.TYPE_STRING, description='Exclude Import Indicator'),
        }
    ))

    def put(self, request):
        '''
        Edit Admin Projected Vacancy
        '''
        result = services.edit_admin_projected_vacancy(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
