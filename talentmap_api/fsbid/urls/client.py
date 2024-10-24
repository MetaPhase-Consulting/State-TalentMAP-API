from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/suggestions/$', views.FSBidClientSuggestionsView.as_view(), name='FSBid-client-suggestions'),
    url(r'^export/$', views.FSBidClientCSVView.as_view(), name="FSBid-client_export"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidClientView.as_view(), name='FSBid-client'),
    url(r'^$', views.FSBidClientListView.as_view(), name='FSBid-client_list'),
    url(r'^client_perdets/$', views.FSBidClientPerdetListView.as_view(), name='FSBid-client_perdets'),
    url(r'^update/$', views.FSBidClientUpdateListView.as_view(), name='FSBid-client_update'),
    url(r'^extra_client_data/$', views.FSBidExtraClientDataView.as_view(), name='FSBid-client_extra_client_data'),
    url(r'^panel/$', views.FSBidClientPanelView.as_view(), name='FSBid-client_panel'),
    url(r'^panel_update/$', views.FSBidClientPanelUpdateView.as_view(), name='FSBid-client_panel_update'),
]

urlpatterns += router.urls
