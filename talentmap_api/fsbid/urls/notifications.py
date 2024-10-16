from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import notifications as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^note_cable/$', views.FSBidNoteCableView.as_view(), name='FSBid-note-cable'),
    url(r'^note_cable/ref/$', views.FSBidNoteCableReferenceView.as_view(), name='FSBid-note-cable-ref'),
    url(r'^cable/$', views.FSBidCableView.as_view(), name='FSBid-cable'),
    url(r'^cable/edit/$', views.FSBidNoteCableEditView.as_view(), name='FSBid-cable-edit'),
    url(r'^rebuild/$', views.FSBidNoteCableRebuildView.as_view(), name='FSBid-rebuild'),
    url(r'^store/$', views.FSBidNoteCableStoreView.as_view(), name='FSBid-store'),
    url(r'^send/$', views.FSBidNoteCableSendView.as_view(), name='FSBid-send'),
    url(r'^ops/wsdl/$', views.FSBidGetOpsWsdlView.as_view(), name='FSBid-get-ops-wsdl'),
    url(r'^ops/data/$', views.FSBidGetOpsDataView.as_view(), name='FSBid-get-ops-data'),
    url(r'^ops/create/$', views.FSBidCreateOpsLogView.as_view(), name='FSBid-create-ops-log'),
    url(r'^ops/update/$', views.FSBidUpdateOpsLogView.as_view(), name='FSBid-update-ops-log'),
    url(r'^gal/$', views.FSBIDGalLookupView.as_view(), name='FSBid-gal-lookup'),
]

urlpatterns += router.urls