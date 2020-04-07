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
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

from talentmap_api.user_profile.models import UserProfile

import talentmap_api.fsbid.services.projected_vacancies as services
import talentmap_api.tasks as tasks

FAVORITES_LIMIT = settings.FAVORITES_LIMIT

class ProjectedVacancyFavoriteListView(APIView):

    permission_classes = (IsAuthenticated,)

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
        ]
    )

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavorite.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        limit = request.query_params.get('limit', 12)
        page = request.query_params.get('page', 1)
        pvs_length = len(pvs)
        
        if pvs_length >= FAVORITES_LIMIT or pvs_length == 150 or pvs_length == 225:
            pos_nums = ','.join(pvs)
            list_pvs = list(map(lambda x: int(x), pvs))
            isAP = False
            returned_ids = services.get_pv_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), 
                                                                 request.META['HTTP_JWT'],
                                                                 f"{request.scheme}://{request.get_host()}")
            tasks.archive_favorites.delay(list_aps, returned_ids, isAP)
        if pvs_length > 0:
            pos_nums = ','.join(pvs)
            return Response(services.get_projected_vacancies(QueryDict(f"id={pos_nums}&limit={limit}&page={page}"),
                                                             request.META['HTTP_JWT'], 
                                                             f"{request.scheme}://{request.get_host()}"))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})

class ProjectedVacancyFavoriteIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavorite.objects.filter(user=user).values_list("fv_seq_num", flat=True)
        return Response(pvs)


class ProjectedVacancyFavoriteActionView(APIView):
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
        user = UserProfile.objects.get(user=self.request.user)
        if ProjectedVacancyFavorite.objects.filter(user=user, fv_seq_num=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the projected vacancy as a favorite
        '''
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavorite.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if len(pvs) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            pvf = ProjectedVacancyFavorite(user=user, fv_seq_num=pk)
            pvf.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the projected vacancy from favorites
        '''
        user = UserProfile.objects.get(user=self.request.user)
        ProjectedVacancyFavorite.objects.get(user=user, fv_seq_num=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
