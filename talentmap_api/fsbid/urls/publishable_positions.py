from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import publishable_positions as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidPublishablePositionsView.as_view(), name='FSBid-publishable-positions'),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidPublishablePositionsActionView.as_view(), name='FSBid-publishable-positions'),
]

urlpatterns += router.urls
