from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bureau_exception_list as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidBureauExceptionsUsersView.as_view(), name='FSBid-bureau-exceptions'),
    url(r'^bureaus/$', views.FSBidBureauExceptionsBureausView.as_view(), name='FSBid-bureau-exceptions-bureaus'),

    url(r'^add/$', views.FSBidBureauExceptionsAddActionView.as_view(), name='FSBid-bureau-exceptions-add'),
    url(r'^update/$', views.FSBidBureauExceptionsUpdateActionView.as_view(), name='FSBid-bureau-exceptions-update'),
    url(r'^delete/$', views.FSBidBureauExceptionsDeleteActionView.as_view(), name='FSBid-bureau-exceptions-delete'),
]

urlpatterns += router.urls
