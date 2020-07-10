import coreapi

from django.http import QueryDict

from django.conf import settings

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.schemas import AutoSchema

from talentmap_api.available_positions.models import AvailablePositionFavoriteTandem
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavoriteTandem

import talentmap_api.fsbid.services.available_positions as services
import talentmap_api.fsbid.services.projected_vacancies as pvservices
import talentmap_api.fsbid.services.common as comservices

import logging
logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT


class AvailablePositionsFilter():
    declared_filters = [
        "exclude_available",
        "exclude_projected",
    ]

    use_api = True

    class Meta:
        fields = "__all__"


class AvailablePositionFavoriteTandemListView(APIView):
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
        Return a list of all of the user's tandem favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        # Set up query set to avoid multiple db calls
        qs = AvailablePositionFavoriteTandem.objects.filter(user=user, archived=False)
        # List of ids to evaluate length and pass to archive service
        aps = qs.values_list("cp_id", flat=True)
        limit = request.query_params.get('limit', 15)
        page = request.query_params.get('page', 1)
        if len(aps) > 0:
            services.archive_favorites(aps, request)
            # Format cp_ids to be passed to get_ap_tandem
            tandem_1_aps = qs.filter(tandem=False).values_list("cp_id", flat=True)
            tandem_2_aps = qs.filter(tandem=True).values_list("cp_id", flat=True)
            # Tandem search returns all results if no params are passed
            # Raise error to alert user to favorite at least 1 position for tandem 1 & 2
            if not (tandem_1_aps and tandem_2_aps):
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            pos_nums_1 = ','.join(tandem_1_aps)
            pos_nums_2 = ','.join(tandem_2_aps)
            return Response(services.get_available_positions_tandem(
                QueryDict(f"id={pos_nums_1}&id-tandem={pos_nums_2}&limit={limit}&page={page}"),
                request.META['HTTP_JWT'],
                f"{request.scheme}://{request.get_host()}"))
        return Response({"count": 0, "next": None, "previous": None, "results": []})


class AvailablePositionFavoriteTandemIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavoriteTandem.objects.filter(user=user, archived=False).values()
        return Response(aps)


class FavoritesTandemCSVView(APIView):

    permission_classes = (IsAuthenticated,)
    filter_class = AvailablePositionsFilter

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("exclude_available", type='boolean', location='query', description='Whether to exclude available positions'),
            coreapi.Field("exclude_projected", type='boolean', location='query', description='Whether to exclude projected vacancies'),
        ]
    )

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the user's favorite positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        data = []

        aps = AvailablePositionFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if len(aps) > 0 and request.query_params.get('exclude_available') != 'true':
            pos_nums = ','.join(aps)
            apdata = services.get_available_positions(QueryDict(f"id={pos_nums}&limit={len(aps)}&page=1"), request.META['HTTP_JWT'])
            data = data + apdata.get('results')
        # TO DO: Change pvs to use tandem once those models are set up
        pvs = ProjectedVacancyFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if len(pvs) > 0 and request.query_params.get('exclude_projected') != 'true':
            pos_nums = ','.join(pvs)
            pvdata = pvservices.get_projected_vacancies(QueryDict(f"id={pos_nums}&limit={len(pvs)}&page=1"), request.META['HTTP_JWT'])
            data = data + pvdata.get('results')

        return comservices.get_ap_and_pv_csv(data, "favorites", True)


class AvailablePositionFavoriteTandemActionView(APIView):
    '''
    Controls the favorite status of a available position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the available position is a favorite

        Returns 204 if the available position is a favorite, otherwise, 404
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        if AvailablePositionFavoriteTandem.objects.filter(user=user, cp_id=pk, archived=False, tandem=is_tandem_two).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the available position as a favorite
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        services.archive_favorites(aps, request)
        aps_after_archive = AvailablePositionFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if len(aps_after_archive) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            AvailablePositionFavoriteTandem.objects.get_or_create(user=user, cp_id=pk, tandem=is_tandem_two)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the available position from favorites
        '''
        is_tandem_two = request.query_params.get('is_tandem_one') == 'false'
        user = UserProfile.objects.get(user=self.request.user)
        AvailablePositionFavoriteTandem.objects.filter(user=user, cp_id=pk, tandem=is_tandem_two).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
