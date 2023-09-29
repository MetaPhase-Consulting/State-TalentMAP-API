from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bureau_exception_list as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidBureauExceptionListView.as_view(), name='FSBid-bureau-exception-list'),
]

urlpatterns += router.urls
