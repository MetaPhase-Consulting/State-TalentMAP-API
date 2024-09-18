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
    
    print("inside FSBidEntryLevelPositionsActionView\n")

    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMember('superuser'))
    '''
    Edit and save an EL Position
    '''

    # json_body is a dictionary that will be passed in from the front end when UI calls the 
    # Django endpoint associated with this view. Hard coding it here for testing.
    # This dictionary will be used to update the EL position in the database.

    json_body1={
                    "PV_API_VERSION_I": "",
                    "PV_AD_ID_I": "",
                    "PV_ACTION_I": "D",
                    "PTYP_CUST_TD_POS_TAB_I": {"Data":[{"POS_SEQ_NUM":774, "EL": "false", "LNA": "false", 
                                                        "FICA": "false", "ELTOML": "true", 
                                                        "MC": "false", "MC_END_DATE": None}]}
    }

    json_body ={
                    "PV_API_VERSION_I": "\"\"",
                    "PV_AD_ID_I": "\"\"",
                    "PV_ACTION_I": "D",
                    "PTYP_CUST_TD_POS_TAB_I": "{\"Data\":[{\"POS_SEQ_NUM\":\"774\",\"EL\": \"false\",\"LNA\": \"false\",\"FICA\": \"false\", \"ELTOML\":\"true\"}, \"MC\": \"false\", \"MC_END_DATE\": null}]}"
        }

    def post(self, request):
        print("inside FSBidEntryLevelPositionsActionView post\n")
        print("request: ", request, "\n")
        print("request.data: ", request.data, "\n")
        print("request.META ('HTTP_JWT will be the jwt token): ", request.META, "\n")
        jwt = request.META['HTTP_JWT']
        # jwt is passed in first when edit_el_positions takes request first and jwt_token as second arg.
        # this is leading to jwt being null and request being the jwt token
        # result = services.edit_el_positions(jwt, request.data)
        result = services.edit_el_positions(data=self.json_body, jwt_token=jwt)
        return Response(result)
