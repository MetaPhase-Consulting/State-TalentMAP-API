from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import org_stats as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidOrgStatsView.as_view(), name='FSBid-org-stats'),
]

urlpatterns += router.urls