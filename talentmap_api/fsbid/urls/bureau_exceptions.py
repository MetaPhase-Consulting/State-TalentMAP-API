from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bureau_exceptions as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidBureauExceptionsView.as_view(), name='FSBid-bureau-exceptions'),
    url(r'^ref_data_bureaus/$', views.FSBidBureauExceptionsRefDataBureausView.as_view(), name='FSBid-bureau-exceptions-ref-data-bureaus'),
    url(r'^metadata/$', views.FSBidBureauExceptionsUserMetaDataView.as_view(), name='FSBid-bureau-exceptions-user-metadata'),
    url(r'^add/$', views.FSBidBureauExceptionsUserAddActionView.as_view(), name='FSBid-bureau-exceptions-user-add'),
    url(r'^update/$', views.FSBidBureauExceptionsUserUpdateActionView.as_view(), name='FSBid-bureau-exceptions-user-update'),
    url(r'^delete/$', views.FSBidBureauExceptionsUserDeleteActionView.as_view(), name='FSBid-bureau-exceptions-user-delete'),
]

urlpatterns += router.urls
