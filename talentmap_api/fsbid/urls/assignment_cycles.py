from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_cycles as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidAssignmentCyclesListView.as_view(), name='FSBid-assignment-cycles-list'),
]

urlpatterns += router.urls
