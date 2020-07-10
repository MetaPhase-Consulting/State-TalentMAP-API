import coreapi

from django.shortcuts import render
from django.http import QueryDict
from django.conf import settings

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.schemas import AutoSchema


from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavoriteTandem

from talentmap_api.user_profile.models import UserProfile

import talentmap_api.fsbid.services.projected_vacancies as services

import logging
logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT


class ProjectedVacancyFavoriteTandemListView(APIView):

    permission_classes = (IsAuthenticated,)

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
            coreapi.Field("is_tandem_one", location='query', type='boolean', description='Specifiy for return results of either tandem one or tandem two'),
        ]
    )

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        # Set up query set to avoid multiple db calls
        qs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False)
        # List of ids to evaluate length and pass to archive service
        pvs = qs.values_list("fv_seq_num", flat=True)
        limit = request.query_params.get('limit', 15)
        page = request.query_params.get('page', 1)
        if len(pvs) > 0:
            services.archive_favorites(pvs, request)
            # Format fv_seq_num to be passed to get_pv_tandem
            tandem_1_pvs = qs.filter(tandem=False).values_list("fv_seq_num", flat=True)
            tandem_2_pvs = qs.filter(tandem=True).values_list("fv_seq_num", flat=True)
            # Tandem search returns all results if no params are passed
            # Raise error to alert user to favorite at least 1 position for tandem 1 & 2
            if not (tandem_1_pvs and tandem_2_pvs):
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            pos_nums_1 = ','.join(tandem_1_pvs)
            pos_nums_2 = ','.join(tandem_2_pvs)
            return Response(services.get_projected_vacancies_tandem(
                QueryDict(f"id={pos_nums_1}&id-tandem={pos_nums_2}&limit={limit}&page={page}"),
                request.META['HTTP_JWT'],
                f"{request.scheme}://{request.get_host()}"))
        return Response({"count": 0, "next": None, "previous": None, "results": []})


class ProjectedVacancyFavoriteTandemIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values()
        return Response(pvs)


class ProjectedVacancyFavoriteTandemActionView(APIView):
    '''
    Controls the favorite status of a projected vacancy

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the projected vacancy is a favorite

        Returns 204 if the projected vacancy is a favorite, otherwise, 404
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        if ProjectedVacancyFavoriteTandem.objects.filter(user=user, fv_seq_num=pk, archived=False, tandem=is_tandem_two).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the projected vacancy as a favorite
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        services.archive_favorites(pvs, request)
        pvs_after_archive = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if len(pvs_after_archive) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            pvf = ProjectedVacancyFavoriteTandem(user=user, fv_seq_num=pk, tandem=is_tandem_two)
            pvf.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the projected vacancy from favorites
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        ProjectedVacancyFavoriteTandem.objects.get(user=user, fv_seq_num=pk, tandem=is_tandem_two).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
