from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import positions as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidPositionView.as_view(), name='FSBid-generic-position'),
    url(r'^$', views.FSBidPositionListView.as_view(), name='FSBid-generic-positions'),
    url(r'^frequent_positions/$', views.FSBidFrequentPositionsView.as_view(), name="FSBid-frequent-positions"),
    url(r'^el_positions/$', views.FSBidEntryLevelPositionsView.as_view(), name="FSBid-el-positions"),
    url(r'^el_positions/filters/$', views.FSBidEntryLevelPositionsFiltersView.as_view(), name='FSBid-el-positions-filters'),
    url(r'^el_positions/save/(?P<pk>[0-9]+)/$', views.FSBidEntryLevelPositionsActionView.as_view(), name='FSBid-el-positions-edit'),
]

urlpatterns += router.urls
