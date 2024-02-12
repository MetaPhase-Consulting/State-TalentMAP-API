from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import manage_bid_seasons as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidManageBidSeasonsView.as_view(), name='FSBid-manage-bid-seasons'),
]

urlpatterns += router.urls
