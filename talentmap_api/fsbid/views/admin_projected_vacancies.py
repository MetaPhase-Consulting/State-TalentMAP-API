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

    permission_classes = (IsAuthenticatedOrReadOnly,)


    def get(self, request, pk):
        '''
        Gets a projected vacancy
        '''
        result = services.get_projected_vacancy_filters(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)



class FSBidAdminProjectedVacancyListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets a projected vacancy
        '''
        result = services.get_projected_vacancy(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)

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


