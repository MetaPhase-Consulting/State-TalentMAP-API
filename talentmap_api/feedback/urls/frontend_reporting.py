from django.conf.urls import url

from talentmap_api.feedback.views import frontend_reporting as views
from talentmap_api.common.urls import get_retrieve, get_list, post_create, delete_destroy

urlpatterns = [
    url(r'^errors/(?P<public_secret>[0-9A-Za-z]+)/$', views.ErrorView.as_view(), name='error-reporting'),
    url(r'^events/(?P<public_secret>[0-9A-Za-z]+)/$', views.EventView.as_view(), name='event-reporting'),
]
