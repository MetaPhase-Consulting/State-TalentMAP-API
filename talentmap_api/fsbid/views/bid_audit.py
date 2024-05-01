import logging
from rest_framework import status
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.bid_audit as services

# from talentmap_api.common.permissions import isDjangoGroupMember
# double check permissions

logger = logging.getLogger(__name__)


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


class FSBidRunBidAuditListView(BaseView):
    '''
    Run Bid Audit, Updates Bid Count
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.run_bid_audit(jwt, request.query_params)

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
