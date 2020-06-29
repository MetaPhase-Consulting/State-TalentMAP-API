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
        is_tandem_one = request.query_params.get('is_tandem_one', None)
        user = UserProfile.objects.get(user=self.request.user)
        if is_tandem_one != None:
            pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False, tandem=is_tandem_one).values_list("fv_seq_num", flat=True)
        else:
            pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        
        limit = request.query_params.get('limit', 12)
        page = request.query_params.get('page', 1)
        if len(pvs) > 0:
            services.archive_favorites(pvs, request)
            pos_nums = ','.join(pvs)
            return Response(services.get_projected_vacancies(QueryDict(f"id={pos_nums}&limit={limit}&page={page}"),
                                                             request.META['HTTP_JWT'],
                                                             f"{request.scheme}://{request.get_host()}"))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})

class ProjectedVacancyFavoriteTandemIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
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
        is_tandem_one = request.query_params.get('is_tandem_one')
        user = UserProfile.objects.get(user=self.request.user)
        if ProjectedVacancyFavoriteTandem.objects.filter(user=user, fv_seq_num=pk, archived=False, tandem=is_tandem_one).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the projected vacancy as a favorite
        '''
        is_tandem_one = request.query_params.get('is_tandem_one')
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        services.archive_favorites(pvs, request)
        pvs_after_archive = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if len(pvs_after_archive) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            pvf = ProjectedVacancyFavoriteTandem(user=user, fv_seq_num=pk, tandem=is_tandem_one)
            pvf.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the projected vacancy from favorites
        '''
        is_tandem_one = request.query_params.get('is_tandem_one')
        user = UserProfile.objects.get(user=self.request.user)
        ProjectedVacancyFavoriteTandem.objects.get(user=user, fv_seq_num=pk, tandem=is_tandem_one).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
