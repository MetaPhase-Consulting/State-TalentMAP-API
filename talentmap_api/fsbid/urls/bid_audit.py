from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bid_audit as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidBidAuditListView.as_view(), name='FSBid-bid-audit-list'),
    url(r'^run/$', views.FSBidRunBidAuditListView.as_view(), name="FSBid-run-audit-list"),
    url(r'^category/$', views.FSBidBidAuditCategoryListView.as_view(), name="FSBid-audit-category-list"),
    url(r'^grade/$', views.FSBidBidAuditGradeListView.as_view(), name="FSBid-audit-grade-list"),
]

urlpatterns += router.urls
