from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bidding_tool as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>\w{2}[0-9]+)/$', views.FSBidBiddingToolView.as_view(), name='FSBid-bidding-tool'),
    url(r'^$', views.FSBidBiddingToolListView.as_view(), name='FSBid-bidding-tool-list'),
    url(r'^edit/$', views.FSBidBiddingToolEditView.as_view(), name='FSBid-bidding-tool-edit'),
    url(r'^create/$', views.FSBidBiddingToolCreateView.as_view(), name='FSBid-bidding-tool-create'),
    url(r'^delete/$', views.FSBidBiddingToolDeleteView.as_view(), name='FSBid-bidding-tool-delete'),
]

urlpatterns += router.urls