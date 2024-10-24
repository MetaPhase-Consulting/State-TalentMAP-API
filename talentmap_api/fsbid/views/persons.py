from rest_condition import Or
from rest_framework.response import Response

from talentmap_api.common.permissions import isDjangoGroupMember
import talentmap_api.fsbid.services.persons as services
from talentmap_api.fsbid.views.base import BaseView

class FSBidPersonsView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    def get(self, request, pk):
        '''
        Get a single employee data from v3/persons by perdetseqnum
        '''
        return Response(services.get_persons(pk, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))
