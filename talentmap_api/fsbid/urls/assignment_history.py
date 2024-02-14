from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_history as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAssignmentHistoryListView.as_view(), name="assignment-history-list"),
    url(r'^(?P<pk>[0-9]+)/alt/$', views.FSBidAltAssignmentHistoryListView.as_view(), name="alt-assignment-history-list"),
    url(r'^(?P<pk>[0-9]+)/assignment/(?P<asg_id>[0-9]+)/$', views.FSBidAssignmentReferenceView.as_view(), name="assignment-ref-data"),
    url(r'^$', views.FSBidPrivateAssignmentHistoryListView.as_view(), name="private-assignment-history-list"),
]

urlpatterns += router.urls
