import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from rest_framework.response import Response
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.reference as services
import talentmap_api.fsbid.services.common as common

TP_ROOT = settings.TP_API_URL

logger = logging.getLogger(__name__)


class FSBidDangerPayView(BaseView):
    uri = "v1/posts/dangerpays"
    mapping_function = services.fsbid_danger_pay_to_talentmap_danger_pay


class FSBidCyclesView(BaseView):
    uri = "v1/cycles"
    mapping_function = services.fsbid_cycles_to_talentmap_cycles


class FSBidBureausView(BaseView):
    uri = "v1/fsbid/bureaus"
    mapping_function = services.fsbid_bureaus_to_talentmap_bureaus


class FSBidDifferentialRatesView(BaseView):
    uri = "v1/posts/differentialrates"
    mapping_function = services.fsbid_differential_rates_to_talentmap_differential_rates


class FSBidGradesView(BaseView):
    uri = "v1/references/grades"
    mapping_function = services.fsbid_grade_to_talentmap_grade


class FSBidLanguagesView(BaseView):
    uri = "v1/references/languages"
    mapping_function = services.fsbid_languages_to_talentmap_languages


class FSBidTourOfDutiesView(BaseView):
    uri = "v1/posts/tourofduties"
    mapping_function = services.fsbid_tour_of_duties_to_talentmap_tour_of_duties


class FSBidToursOfDutyView(BaseView):
    uri = "v1/references/tours-of-duty"
    mapping_function = services.fsbid_tours_of_duty_to_talentmap_tours_of_duty


class FSBidCodesView(BaseView):
    uri = "v1/references/skills"
    mapping_function = services.fsbid_codes_to_talentmap_codes


class FSBidLocationsView(BaseView):
    uri = "v1/references/Locations"
    mapping_function = services.fsbid_locations_to_talentmap_locations

class FSBidGSALocationsView(BaseView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request):
        """
        Return a list of filterable reference data for GSA locations
        """
        return Response(services.get_gsa_locations(request.query_params, request.META['HTTP_JWT']))


class FSBidConesView(BaseView):
    uri = "v1/references/skills"
    mapping_function = services.fsbid_codes_to_talentmap_cones

    def modCones(self, results):
        results = list(results)
        values = set(map(lambda x: x['category'], results))

        newlist, codes = [], []
        for cone in values:
            for info in results:
                if info['category'] == cone:
                    codes.append({'code': info['code'], 'id': info['id'], 'description': info['description']})

            newlist.append({'category': cone, 'skills': codes})
            codes = []
        return newlist

    mod_function = modCones


class FSBidClassificationsView(BaseView):
    mapping_function = services.fsbid_classifications_to_talentmap_classifications

    def get(self, request):
        results = common.get_results('', {}, None, request.META['HTTP_JWT'], self.mapping_function, TP_ROOT)
        results = self.modClassifications(results)
        return Response(results)

    # BTP return some duplicated objects with unique bid season references
    # This nests those unique values in an array under one object to aggregate the duplicated data
    # As of 03/21, the only applicable edge cases are `Tenured 4` and `Differential Bidder`
    def modClassifications(self, results):
        duplicate_results = list(results)
        unique_codes = set(map(lambda x: x['code'], duplicate_results))

        nested_results, seasons, classification_text, glossary_term = [], [], '', ''
        for code in unique_codes:
            for classification in duplicate_results:
                if classification['code'] == code:
                    classification_text = classification['text']
                    glossary_term = classification['glossary_term']
                    season_txt = classification['season_text'].split(' - ')
                    seasons.append({
                        'id': classification['id'],
                        'season_text': season_txt[1] if len(season_txt) > 1 else None
                    })

            nested_results.append({
                'code': code,
                'text': classification_text,
                'seasons': seasons,
                'glossary_term': glossary_term
            })
            seasons, classification_text = [], ''
        return nested_results


class FSBidPostIndicatorsView(BaseView):
    uri = "v1/posts/attributes?codeTableName=PostIndicatorTable"
    mapping_function = services.fsbid_post_indicators_to_talentmap_indicators


class FSBidUnaccompaniedStatusView(BaseView):
    uri = "v1/posts/attributes?codeTableName=UnaccompaniedTable"
    mapping_function = services.fsbid_us_to_talentmap_us


class FSBidCommuterPostsView(BaseView):
    uri = "v1/posts/attributes?codeTableName=CommuterPostTable"
    mapping_function = services.fsbid_commuter_posts_to_talentmap_commuter_posts

class FSBidTravelFunctionsView(BaseView):

    def get(self, request):
        """
        Return a list of reference data for all travel-functions
        """
        return Response(services.get_travel_functions(request.query_params, request.META['HTTP_JWT']))
