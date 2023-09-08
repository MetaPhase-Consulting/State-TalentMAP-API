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

    def get(self, request):
        '''
        Gets admin projected vacancy filters
        '''
        result = services.get_admin_projected_vacancy_filters(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidAdminProjectedVacancyLanguageOffsetsView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets admin projected vacancy language offsets
        '''
        result = services.get_admin_projected_vacancy_language_offsets(request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)



class FSBidAdminProjectedVacancyListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets admin projected vacancies
        '''
        result = services.get_admin_projected_vacancies(request, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


