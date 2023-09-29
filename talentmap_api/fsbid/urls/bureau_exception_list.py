from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import publishable_positions as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidBureauExceptionListView.as_view(), name='FSBid-bureau-exception-list'),
]

urlpatterns += router.urls
