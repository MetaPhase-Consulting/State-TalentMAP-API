import logging
import coreapi

from rest_condition import Or
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import talentmap_api.fsbid.services.admin_projected_vacancies as services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)

class FSBidAdminProjectedVacancyFiltersView(APIView):

    # ======================== Get PV Filters ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Gets Filters for Admin Projected Vacancies
        '''
        result = services.get_admin_projected_vacancy_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

class FSBidAdminProjectedVacancyLangOffsetOptionsView(APIView):

    # ======================== Get Language Offset Options ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    def get(self, request):
        '''
        Gets Language Offset Options for Admin Projected Vacancies
        '''
        result = services.get_admin_projected_vacancy_lang_offset_options(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)
    
class FSBidAdminProjectedVacancyListView(APIView):

    # ======================== Get PV List ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Page'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Limit'),
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

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), )]

    def put(self, request):
        '''
        Edit Admin Projected Vacancy
        '''
        result = services.edit_admin_projected_vacancy(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FSBidAdminProjectedVacancyEditLangOffsetsView(APIView):
    
    # ======================== Edit PV Language Offsets ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'position_seq_num': openapi.Schema(type=openapi.TYPE_STRING, description='Position Seq Num'),
            'language_offset_summer': openapi.Schema(type=openapi.TYPE_STRING, description='Language Offset Summer'),
            'language_offset_winter': openapi.Schema(type=openapi.TYPE_STRING, description='Language Offset Winter'),
        }
    ))

    def put(self, request):
        '''
        Edit Admin Projected Vacancy Language Offsets
        '''
        result = services.edit_admin_projected_vacancy_lang_offsets(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidAdminProjectedVacancyEditCapsuleDescView(APIView):
    
    # ======================== Edit PV Capsule Description ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'position_seq_num': openapi.Schema(type=openapi.TYPE_STRING, description='Position Seq Num'),
            'capsule_description': openapi.Schema(type=openapi.TYPE_STRING, description='Capsule Description'),
            'updater_id': openapi.Schema(type=openapi.TYPE_STRING, description='Updater ID'),
            'updated_date': openapi.Schema(type=openapi.TYPE_STRING, description='Updated Date'),
        }
    ))

    def put(self, request):
        '''
        Edit Admin Projected Vacancy Capsule Description
        '''
        result = services.edit_admin_projected_vacancy_capsule_desc(request.data, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class FSBidAdminProjectedVacancyLangOffsetsView(APIView):
    
    # ======================== Get PV Language Offsets ========================

    permission_classes = [IsAuthenticated, Or(isDjangoGroupMember('bureau_user'), isDjangoGroupMember('superuser'), ) ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("position_numbers", openapi.IN_QUERY, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='Position Number Text Array'),
        ]
    )

    def get(self, request):
        '''
        Get Admin Projected Vacancy Language Offsets
        '''
        result = services.get_admin_projected_vacancy_lang_offsets(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)
