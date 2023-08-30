import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_condition import Or
from talentmap_api.common.permissions import isDjangoGroupMember


from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.panel as services

logger = logging.getLogger(__name__)

base_parameters = [
    # Pagination
    openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
    openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
    openapi.Parameter("current-bureaus", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Current bureaus, comma separated'),
    openapi.Parameter("handshake-bureaus", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake bureaus, comma separated'),
    openapi.Parameter("current-organizations", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Current organizations, comma separated'),
    openapi.Parameter("handshake-organizations", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake organizations, comma separated'),
    openapi.Parameter("ted-start", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TED start date'),
    openapi.Parameter("ted-end", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TED end date'),
    openapi.Parameter("cdo", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='CDO codes, comma separated'),
    openapi.Parameter("handshake", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake codes, comma separated (Y, N)'),
]

class PanelCategoriesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel categories
        '''
        return Response(services.get_panel_categories(request.query_params, request.META['HTTP_JWT']))

class PanelDatesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel dates
        '''
        return Response(services.get_panel_dates(request.query_params, request.META['HTTP_JWT']))

class PanelStatusesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel statuses
        '''
        return Response(services.get_panel_statuses(request.query_params, request.META['HTTP_JWT']))

class PanelTypesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel types
        '''
        return Response(services.get_panel_types(request.query_params, request.META['HTTP_JWT']))

class PanelMeetingsView(BaseView):
    # check perms assumptions
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Sort Panel meetings'),
            openapi.Parameter("type", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting type.'),
            openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting status.'),
            openapi.Parameter("panel-date-start", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting date start.'),
            openapi.Parameter("panel-date-end", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting date end.'),
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting seq num.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel meetings
        '''
        return Response(services.get_panel_meetings(request.query_params, request.META['HTTP_JWT']))

    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'pm_seq_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting ID'),
            'pm_virtual': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Virtual'),
            'pm_create_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting Created ID'),
            'pm_create_date': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Created Date'),
            'pm_update_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting Updated ID'),
            'pm_update_date': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Updated Date'),
            'pms_code': openapi.Schema(type=openapi.TYPE_STRING, description='PMS Code'),
            'pmt_code': openapi.Schema(type=openapi.TYPE_STRING, description='PMT Code'),
            'pmt_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='PMT Description'),
            'pms_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='PMS Description'),
            'panelMeetingDates': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    'pm_seq_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting ID'),
                    'mdt_code': openapi.Schema(type=openapi.TYPE_STRING, description='MDT Code'),
                    'pmd_dttm': openapi.Schema(type=openapi.TYPE_STRING, description='Date'),
                    'mdt_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
                    'mdt_order_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order Number'),
                }
            ), description='Panel Meeting Dates'),
        }
    ))

    def put(self, request):
        '''
        Edit panel meeting
        '''
        return Response(services.edit_panel(request.data, request.META['HTTP_JWT']))
    
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'pm_seq_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting ID'),
            'pm_virtual': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Virtual'),
            'pm_create_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting Created ID'),
            'pm_create_date': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Created Date'),
            'pm_update_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting Updated ID'),
            'pm_update_date': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Updated Date'),
            'pms_code': openapi.Schema(type=openapi.TYPE_STRING, description='PMS Code'),
            'pmt_code': openapi.Schema(type=openapi.TYPE_STRING, description='PMT Code'),
            'pmt_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='PMT Description'),
            'pms_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='PMS Description'),
            'panelMeetingDates': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    'pm_seq_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting ID'),
                    'mdt_code': openapi.Schema(type=openapi.TYPE_STRING, description='MDT Code'),
                    'pmd_dttm': openapi.Schema(type=openapi.TYPE_STRING, description='Date'),
                    'mdt_desc_text': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
                    'mdt_order_num': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order Number'),
                }
            ), description='Panel Meeting Dates'),
        }
    ))

    def post(self, request):
        '''
        Create panel meeting
        '''
        try:
            services.create_panel(request.data, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.info(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class PanelMeetingsCSVView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    @swagger_auto_schema(manual_parameters=base_parameters)

    def get(self, request):
        '''
        Exports all Panel Meetings to CSV format
        '''
        return services.get_panel_meetings_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")


class PostPanelView(BaseView):
    # check perms assumptions
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting seq num.'),
        ])

    def get(self, request):
        '''
        Gets post panel
        '''
        return Response(services.get_post_panel(request.query_params, request.META['HTTP_JWT']))
    
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    # TODO: Rename fields with TM query
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'QRY_MODPOSTPNL_REF': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    'PMT_DESC_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='PMT Description Text'),
                    'PMI_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='PMI Panel Meeting ID'),
                    'PMI_OFFICIAL_ITEM_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='PMI Official Item Number'),
                    'AI_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='AI Sequence Number'),
                    'AI_LABEL_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='AI Label Text'),
                    'AI_VALID_IND': openapi.Schema(type=openapi.TYPE_STRING, description='AI Valid Ind'),
                    'AIS_ABBR_DESC_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='AIS Abbreviation Description Text'),
                    'AIS_DESC_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='AIS Description Text'),
                    'EMP_FULL_NAME': openapi.Schema(type=openapi.TYPE_STRING, description='Employee Full Name'),
                    'AI_UPDATE_ID': openapi.Schema(type=openapi.TYPE_INTEGER, description='AI Update ID'),
                    'AI_UPDATE_DATE': openapi.Schema(type=openapi.TYPE_STRING, description='AI Update Date'),
                    'AI_AIS_CODE': openapi.Schema(type=openapi.TYPE_STRING, description='AI AIS Code'),
                    'PM_PMT_CODE': openapi.Schema(type=openapi.TYPE_STRING, description='PM PMT Code'),
                    'VIRTUAL_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='Virtual Text'),
                    'PMD_DTTM': openapi.Schema(type=openapi.TYPE_STRING, description='PMD DTTM'),
                    'MIC_DESC_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='MIC Description Text'),
                    'AI_CORRECTION_TEXT_IND': openapi.Schema(type=openapi.TYPE_STRING, description='AI Correction Text Ind'),
                    'MAX_AIH_HOLD_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='Max AIH Hold Number'),
                    'MAX_AIH_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='Max AIH Sequence Number'),
                    'MAX_AHT_CODE': openapi.Schema(type=openapi.TYPE_INTEGER, description='Max AHT Code'),
                    'MAX_AIH_HOLD_COMMENT_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='Max AIH Hold Comment Text'),
                    'AIH_SEQ_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='AIH Sequence Number'),
                    'AHT_CODE': openapi.Schema(type=openapi.TYPE_STRING, description='AHT Code'),
                    'AIH_HOLD_NUM': openapi.Schema(type=openapi.TYPE_INTEGER, description='AIH Hold Number'),
                    'AIH_HOLD_COMMENT_TEXT': openapi.Schema(type=openapi.TYPE_STRING, description='AIH Hold Comment Text'),
                    'AIH_UPDATE_ID': openapi.Schema(type=openapi.TYPE_INTEGER, description='AIH Update ID'),
                    'AIH_UPDATE_DATE': openapi.Schema(type=openapi.TYPE_STRING, description='AIH Update Date'),
                }
            ), description='Post Panel Processing'),
        }
    ))

    def put(self, request):
        '''
        Edit post panel
        '''
        return Response(services.edit_post_panel(request.data, request.META['HTTP_JWT']))