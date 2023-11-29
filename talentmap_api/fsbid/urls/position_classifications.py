from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import position_classifications as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>\w{2,3}[0-9]+)/$', views.FSBidPositionClassificationsView.as_view(), name='FSBid-position-classifications'),
    url(r'^edit/$', views.FSBidPositionClassificationsActionView.as_view(), name='FSBid-position-classifications-edit'),
]

urlpatterns += router.urls