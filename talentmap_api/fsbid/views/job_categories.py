import logging

from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
import talentmap_api.fsbid.services.job_categories as services

logger = logging.getLogger(__name__)

class FSBidJobCategoriesListView(BaseView):
    '''
    Get a list of all Job Categories
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_job_categories_data(jwt, request.query_params)
        return Response(result)

class FSBidJobCategorySkillsListView(BaseView):
    '''
    Get a list of all Skills associated with a Job Category
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_job_category_skills(jwt, request.query_params)
        return Response(result)
