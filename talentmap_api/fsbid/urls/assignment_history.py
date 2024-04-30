from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_history as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAssignmentHistoryListView.as_view(), name="assignment-history-list"),
    url(r'^(?P<pk>[-\w]+)/assignments-separations/$', views.FSBidAltAssignmentsSeparationsListView.as_view(), name="alt-assignments-separations-list"),
    url(r'^(?P<pk>[-\w]+)/assignments/$', views.FSBidAltAssignmentsBaseView.as_view(), name="alt-assignments-base"),
    url(r'^(?P<pk>[-\w]+)/separations/$', views.FSBidAltSeparationsListBaseView.as_view(), name="alt-separations-base"),
    url(r'^(?P<pk>[-\w]+)/assignments/(?P<id>[-\w]+)/$', views.FSBidAltAssignmentsActionView.as_view(), name="alt-assignments-actions"),
    url(r'^(?P<pk>[-\w]+)/separations/(?P<id>[-\w]+)/$', views.FSBidAltSeparationsListActionView.as_view(), name="alt-separations-actions"),
    url(r'^$', views.FSBidPrivateAssignmentHistoryListView.as_view(), name="private-assignment-history-list"),
]

urlpatterns += router.urls
