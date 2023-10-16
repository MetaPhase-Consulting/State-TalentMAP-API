from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import admin_panel as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^remark/$', views.CreateRemarkView.as_view(), name='administration-createremark'),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidPanelMeetingView.as_view(), name='FSBID-panel-meeting'),
    url(r'^edit/$', views.FSBidPanelMeetingActionView.as_view(), name='FSBID-panel-meeting-actions'),
    url(r'^post_panel/(?P<pk>[0-9]+)/$', views.FSBidPostPanelView.as_view(), name='FSBid-post-panel-processing'),
    url(r'^post_panel/edit/$', views.FSBidPostPanelActionView.as_view(), name='FSBid-post-panel-processing-actions'),
    url(r'^run/preliminary/(?P<pk>[0-9]+)/$', views.FSBidRunPreliminaryActionView.as_view(), name='FSBID-run-preliminary-action'),
    url(r'^run/addendum/(?P<pk>[0-9]+)/$', views.FSBidRunAddendumActionView.as_view(), name='FSBID-run-addendum-action'),
    url(r'^run/post_panel/(?P<pk>[0-9]+)/$', views.FSBidRunPostPanelActionView.as_view(), name='FSBID-run-post-panel-action'),
]

urlpatterns += router.urls
