import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.filters import ProjectedVacancyFilter

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.projected_vacancies as services

from talentmap_api.common.common_helpers import in_superuser_group
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class FSBidProjectedVacanciesListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Projected Vacancies ids"),
            openapi.Parameter("is_available_in_bidseason", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id'),
            openapi.Parameter("is_domestic", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Is the position domestic? (true/false)'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Post id'),
            openapi.Parameter("position__post__danger_pay__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Danger pay'),
            openapi.Parameter("position__post__differential_rate__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Diff. Rate'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),
            openapi.Parameter("position__us_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/unaccompaniedstatuses/'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all projected vacancies
        '''
        return Response(services.get_projected_vacancies(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidProjectedVacanciesTandemListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("getCount", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Results Count'),

            # Tandem 1
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Projected Vacancies ids"),
            openapi.Parameter("is_available_in_bidseason", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),

            # Common
            openapi.Parameter("is_domestic", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Is the position domestic? (true/false)'),
            openapi.Parameter("position__post__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Post id'),
            openapi.Parameter("position__post__danger_pay__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Danger pay'),
            openapi.Parameter("position__post__differential_rate__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Diff. Rate'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__us_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/unaccompaniedstatuses/'),
            openapi.Parameter("position__cpn_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/commuterposts/'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Text search'),

            # Tandem 2
            # Exclude post, post differentials, is_domestic
            openapi.Parameter("id-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids - tandem"),
            openapi.Parameter("is_available_in_bidseason-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id - tandem'),
            openapi.Parameter("language_codes-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code - tandem'),
            openapi.Parameter("position__bureau__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code - tandem'),
            openapi.Parameter("position__grade__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code - tandem'),
            openapi.Parameter("position__position_number__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code - tandem'),
            openapi.Parameter("position__skill__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code - tandem'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all tandem projected vacancies
        '''
        return Response(services.get_projected_vacancies_tandem(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidProjectedVacancyView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets a projected vacancy
        '''
        result = services.get_projected_vacancy(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidProjectedVacancyEditView(BaseView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'bidcycle': openapi.Schema(type=openapi.TYPE_OBJECT,
                properties={
                    'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Active'),
                    'cycle_deadline_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Deadline Date'),
                    'cycle_end_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle End Date'),
                    'cycle_start_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Start Date'),
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bid Cycle ID'),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name'),
                }
            , description='Bid Cycle'),
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Projected Vacancy ID'),
            'isConsumable': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Consumable'),
            'isDifficultToStaff': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Difficult To Staff'),
            'isEFMInside': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='EFM Inside'),
            'isEFMOutside': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='EFM Outside'),
            'isServiceNeedDifferential': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Service Need Differential'),
            'position': openapi.Schema(type=openapi.TYPE_OBJECT,
                properties={
                    'assignee': openapi.Schema(type=openapi.TYPE_STRING, description='Assignee'),
                    'availability': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'availability': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Availability'),
                            'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason'),
                        }
                    , description='Availability'),
                    'bid_cycle_statuses': openapi.Schema(type=openapi.TYPE_STRING, description='Leg Action Type'),
                    'bureau': openapi.Schema(type=openapi.TYPE_STRING, description='Bureau'),
                    'commuterPost': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
                            'frequency': openapi.Schema(type=openapi.TYPE_STRING, description='Frequency'),
                        }
                    , description='Commuter Post'),
                    'current_assignment': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'estimated_end_date': openapi.Schema(type=openapi.TYPE_STRING, description='Estimated End Date'),
                            'user': openapi.Schema(type=openapi.TYPE_STRING, description='User'),
                        }
                    , description='Current Assignment'),
                    'description': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content'),
                            'date_updated': openapi.Schema(type=openapi.TYPE_STRING, description='Date Updated'),
                        }
                    , description='Description'),
                    'grade': openapi.Schema(type=openapi.TYPE_STRING, description='Grade'),
                    'languages': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'language': openapi.Schema(type=openapi.TYPE_STRING, description='Language'),
                            'reading_proficiency': openapi.Schema(type=openapi.TYPE_STRING, description='Reading Proficiency'),
                            'representation': openapi.Schema(type=openapi.TYPE_STRING, description='Representation'),
                            'spoken_proficiency': openapi.Schema(type=openapi.TYPE_STRING, description='Spoken Proficiency'),
                        }
                    ), description='Languages'),
                    'latest_bidcycle': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Active'),
                            'cycle_deadline_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Deadline Date'),
                            'cycle_end_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle End Date'),
                            'cycle_start_date': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Start Date'),
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bid Cycle ID'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name'),
                        }
                    , description='Latest Bid Cycle'),
                    'organization': openapi.Schema(type=openapi.TYPE_STRING, description='Organization'), 
                    'position_number': openapi.Schema(type=openapi.TYPE_STRING, description='Position Number'), 
                    'post': openapi.Schema(type=openapi.TYPE_OBJECT,
                        properties={
                            'danger_pay': openapi.Schema(type=openapi.TYPE_INTEGER, description='Danger Pay'),
                            'differential_rate': openapi.Schema(type=openapi.TYPE_INTEGER, description='Differential Rate'),
                            'location': openapi.Schema(type=openapi.TYPE_OBJECT,
                                properties={
                                    'city': openapi.Schema(type=openapi.TYPE_INTEGER, description='City'),
                                    'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='Code'),
                                    'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country'),
                                    'state': openapi.Schema(type=openapi.TYPE_STRING, description='State'),
                                }
                            , description='Location'),
                            'obc_id': openapi.Schema(type=openapi.TYPE_STRING, description='OBC ID'),
                            'post_bidding_considerations_url': openapi.Schema(type=openapi.TYPE_STRING, description='Post Bidding Considerations URL'),
                            'post_overview_url': openapi.Schema(type=openapi.TYPE_STRING, description='Post Overview URL'),
                            'tour_of_duty': openapi.Schema(type=openapi.TYPE_STRING, description='Tour of Duty'),
                        }
                    , description='Post'),
                    'skill': openapi.Schema(type=openapi.TYPE_STRING, description='Skill'), 
                    'skill_code': openapi.Schema(type=openapi.TYPE_STRING, description='Skill Code'), 
                    'skill_secondary': openapi.Schema(type=openapi.TYPE_STRING, description='Skill Secondary'), 
                    'skill_secondary_code': openapi.Schema(type=openapi.TYPE_STRING, description='Skill Secondary Code'), 
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title'), 
                    'tour_of_duty': openapi.Schema(type=openapi.TYPE_STRING, description='Tour of Duty'), 
                }
            , description='Position'),
            'tandem_nbr': openapi.Schema(type=openapi.TYPE_STRING, description='Tandem Number'),
            'ted': openapi.Schema(type=openapi.TYPE_STRING, description='TED'),
            'unaccompaniedStatus': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Unaccompanied Status'),
        }
    ))

    def put(self, request):
        '''
        Edit projected vacancy
        '''
        return Response(services.edit_projected_vacancy(request.data, request.META['HTTP_JWT']))


class FSBidProjectedVacanciesCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    def get(self, request, *args, **kwargs):
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_projected_vacancies_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)


class FSBidProjectedVacanciesTandemCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    def get(self, request, *args, **kwargs):
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_projected_vacancies_tandem_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)
