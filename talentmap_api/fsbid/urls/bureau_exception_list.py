from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bureau_exception_list as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidBureauExceptionListView.as_view(), name='FSBid-bureau-exception-list'),
    url(r'^edit/$', views.FSBidSaveBureauExceptionListActionView.as_view(), name='FSBid-bureau-exception-list-add'),
    url(r'^edit/$(?P<pk>[0-9]+)/$', views.FSBidBureauExceptionListActionView.as_view(), name='FSBid-bureau-exception-list-edit'),
    url(r'^bureaus/$', views.FSBidBureauExceptionBureauListView.as_view(), name='FSBid-bureau-exception-list-bureaus'),
]

urlpatterns += router.urls
