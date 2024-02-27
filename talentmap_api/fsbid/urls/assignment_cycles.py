from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_cycles as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidAssignmentCyclesListView.as_view(), name='FSBid-assignment-cycles-list'),
    url(r'^create/$', views.FSBidAssignmentCyclesCreateView.as_view(), name="FSBid-assignment-cycles-create"),
    url(r'^update/$', views.FSBidAssignmentCyclesUpdateView.as_view(), name="FSBid-assignment-cycles-update"),
    url(r'^post/(?P<pk>[0-9]+)/$', views.FSBidAssignmentCyclesPostPosView.as_view(), name="FSBid-assignment-cycles-post-pos"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAssignmentCycleListView.as_view(), name="FSBid-assignment-cycle-list"),
]

urlpatterns += router.urls
