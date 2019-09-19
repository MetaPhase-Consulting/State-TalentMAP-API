import coreapi

from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.schemas import AutoSchema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.fsbid.filters import AvailablePositionsFilter

import talentmap_api.fsbid.services.available_positions as services

import logging
logger = logging.getLogger(__name__)

class BaseView(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

class FSBidAvailablePositionsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("is_available_in_bidcycle", location='query', description='Bid Cycle id'),
            coreapi.Field("position__skill__code__in", location='query', description='Skill Code'),
            coreapi.Field("position__grade__code__in", location='query', description='Grade Code'),
            coreapi.Field("position__bureau__code__in", location='query', description='Bureau Code'),
            coreapi.Field("is_domestic", location='query', description='Is the position domestic? (true/false)'),
            coreapi.Field("position__post__in", location='query', description='Post id'),
            coreapi.Field("position__post__tour_of_duty__code__in", location='query', description='TOD code'),
            coreapi.Field("position__post__differential_rate__in", location='query', description='Diff. Rate'),
            coreapi.Field("language_codes", location='query', description='Language code'),
            coreapi.Field("position__post__danger_pay__in", location='query', description='Danger pay'),
            coreapi.Field("q", location='query', description='Text search'),
        ]
    )
    def get(self, request, *args, **kwargs):
        '''
        Gets all available positions
        '''
        return Response(services.get_available_positions(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidAvailablePositionsCSVView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        '''
        Gets all available positions
        '''
        return services.get_available_positions_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")


class FSBidAvailablePositionView(BaseView):
    
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets an available position
        '''
        return Response(services.get_available_position(pk, request.META['HTTP_JWT']))


class FSBidAvailablePositionsSimilarView(BaseView):
    
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets similar available positions to the position provided
        '''
        return Response(services.get_similar_available_positions(pk, request.META['HTTP_JWT']))
