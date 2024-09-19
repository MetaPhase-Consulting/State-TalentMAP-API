import logging
import coreapi

from rest_condition import Or
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
import talentmap_api.fsbid.services.positions as services


logger = logging.getLogger(__name__)


class FSBidPositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets generic position
        '''
        result = services.get_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPositionListView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='pos_seq_num of position.'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("position_num", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Position number.'),
        ])

    def get(self, request):
        '''
        Gets generic positions
        '''
        result = services.get_positions(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidFrequentPositionsView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    def get(self, request):
        """
        Return a list of reference data for all frequent positions
        """
        return Response(services.get_frequent_positions(request.query_params, request.META['HTTP_JWT']))

class FSBidEntryLevelPositionsView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMember('superuser'))

    def get(self, request):
        """
        Get a list of all Entry Level Positions
        """
        return Response(services.get_el_positions(request.query_params, request.META['HTTP_JWT']))

class FSBidEntryLevelPositionsFiltersView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMember('superuser'))

    def get(self, request):
        """
        Get Entry Level Positions Filters
        """
        return Response(services.get_el_positions_filters(request.query_params, request.META['HTTP_JWT']))

class FSBidEntryLevelPositionsActionView(BaseView):
    '''
    Edit and save an EL Position
    '''
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMember('superuser'))

    def post(self, request):
        logger.info("inside FSBidEntryLevelPositionsActionView post\n")
        logger.info("request: ", request, "\n")
        logger.info("request.data: ", request.data, "\n")
        logger.info("request.META ('HTTP_JWT will be the jwt token): ", request.META, "\n")

        # json data passed in from UI. Web Service JSONInput requires "Data" key to be a list of
        # json objects thus the append below
        ui_json = [].append(request.data)

        # Web Service JSON Input for EL Position edit
        ws_json_input = {
                            "PV_API_VERSION_I": "",
                            "PV_AD_ID_I": "",
                            "PV_ACTION_I": "D",
                            "PTYP_CUST_TD_POS_TAB_I": {"Data":ui_json}
                        }
        
        jwt = request.META['HTTP_JWT']
        result = services.edit_el_positions(data=ws_json_input, jwt_token=jwt)
        return Response(result)
