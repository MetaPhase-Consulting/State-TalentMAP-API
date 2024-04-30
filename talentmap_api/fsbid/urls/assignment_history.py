from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_history as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAssignmentHistoryListView.as_view(), name="assignment-history-list"),
    url(r'^(?P<pk>[-\w]+)/assignments-separations/$', views.FSBidMaintainAssignmentsSeparationsListView.as_view(), name="maintain-assignments-separations-list"),
    url(r'^(?P<pk>[-\w]+)/assignments/$', views.FSBidMaintainAssignmentsBaseView.as_view(), name="maintain-assignments-base"),
    url(r'^(?P<pk>[-\w]+)/separations/$', views.FSBidmaintainSeparationsListBaseView.as_view(), name="maintain-separations-base"),
    url(r'^(?P<pk>[-\w]+)/assignments/(?P<id>[-\w]+)/$', views.FSBidMaintainAssignmentsActionView.as_view(), name="maintain-assignments-actions"),
    url(r'^(?P<pk>[-\w]+)/separations/(?P<id>[-\w]+)/$', views.FSBidmaintainSeparationsListActionView.as_view(), name="maintain-separations-actions"),
    url(r'^$', views.FSBidPrivateAssignmentHistoryListView.as_view(), name="private-assignment-history-list"),
]

urlpatterns += router.urls
