import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.bid_audit as services

# from talentmap_api.common.permissions import isDjangoGroupMember
# double check permissions

logger = logging.getLogger(__name__)


class FSBidBidAuditRunView(APIView):
    '''
    Run A Bid Audit 
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.run_bid_audit(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Run Bid Audit Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBidAuditListView(BaseView):
    '''
    Gets the List of Bid Audits
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_bid_audit_data(jwt, request.query_params)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Bid Audits failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidActiveCyclesListView(BaseView):
    '''
    Get Active Cycles for New Bid Audits
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_cycles(jwt, request.query_params)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to get Active Cycles failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditCreateView(APIView):
    '''
    Create a new Bid Audit
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.create_new_audit(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Create New Bid Audit Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditUpdateView(APIView):
    '''
    Update a Bid Audit
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_bid_audit(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update a Bid Audit Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditUpdateCountListView(BaseView):
    '''
    Update Bid Count
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_bid_count(jwt, request.query_params)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to run Bid Audit failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditCategoryListView(BaseView):
    '''
    Get List of Positions In Category for a Cycle
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_in_category(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Bid Audit data failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditGradeListView(BaseView):
    '''
    Get a List of Positions At Grade for a Cycle
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_at_grade(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Post Open Positions failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditCategoryOptionsListView(BaseView):
    '''
    Get List of Options for In Category designation
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_in_category_options(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Bid Audit Category data failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditCategoryCreateListView(APIView):
    '''
    Create a new In Category
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.create_new_in_category(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Create New In Category Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditGradeOptionsListView(BaseView):
    '''
    Get List of Options for At Grade designation
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_at_grade_options(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call for Bid Audit Grade data failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditGradeCreateListView(APIView):
    '''
    Create a new At Grade
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.create_new_at_grade(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Create New At Grade Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditUpdateGradeListView(APIView):
    '''
    Modify existing At Grade
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_at_grade(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update At Grade Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditUpdateCategoryListView(APIView):
    '''
    Modify existing In Category
    '''

    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.update_in_category(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Update In Category Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditDeleteGradeListView(APIView):
    '''
    Delete existing At Grade relationship
    '''

    def delete(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.delete_at_grade(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Delete At Grade Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidBidAuditDeleteCategoryListView(APIView):
    '''
    Delete existing In Category relationship
    '''

    def delete(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.delete_in_category(jwt, request.data)

        if result is None or 'return_code' in result and result['return_code'] != 0:
            logger.error(f"Fsbid call to Delete In Category Failed.")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)
