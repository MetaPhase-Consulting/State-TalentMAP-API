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
    url(r'^ops/get/$', views.FSBidGetOpsView.as_view(), name='FSBid-get-ops'),
    url(r'^ops/list/$', views.FSBidListOpsView.as_view(), name='FSBid-list-ops'),
    url(r'^ops/insert/$', views.FSBidInsertOpsView.as_view(), name='FSBid-insert-ops'),
    url(r'^ops/update/$', views.FSBidUpdateOpsView.as_view(), name='FSBid-update-ops'),
]

urlpatterns += router.urls