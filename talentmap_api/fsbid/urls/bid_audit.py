from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bid_audit as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidBidAuditListView.as_view(), name='FSBid-bid-audit-list'),
    url(r'^run/$', views.FSBidBidAuditRunView.as_view(), name="FSBid-run-bid-audit-list"),
    url(r'^cycles/$', views.FSBidActiveCyclesListView.as_view(), name='FSBid-active-cycles-list'),
    url(r'^update/$', views.FSBidBidAuditUpdateView.as_view(), name='FSBid-update-audit'),
    url(r'^update_count/$', views.FSBidBidAuditUpdateCountListView.as_view(), name="FSBid-update-bid-count-list"),
    url(r'^update_grade/$', views.FSBidBidAuditUpdateGradeListView.as_view(), name="FSBid-update-grades-list"),
    url(r'^update_category/$', views.FSBidBidAuditUpdateCategoryListView.as_view(), name="FSBid-update-category-list"),
    url(r'^delete_grade/$', views.FSBidBidAuditDeleteGradeListView.as_view(), name="FSBid-delete-grades-list"),
    url(r'^delete_category/$', views.FSBidBidAuditDeleteCategoryListView.as_view(), name="FSBid-delete-category-list"),
    url(r'^create/$', views.FSBidBidAuditCreateView.as_view(), name="FSBid-create-bid-audit"),
    url(r'^category/$', views.FSBidBidAuditCategoryListView.as_view(), name="FSBid-audit-category-list"),
    url(r'^options/category/$', views.FSBidBidAuditCategoryOptionsListView.as_view(), name="FSBid-audit-category-options-list"),
    url(r'^create/category/$', views.FSBidBidAuditCategoryCreateListView.as_view(), name="FSBid-audit-category-create-list"),
    url(r'^grade/$', views.FSBidBidAuditGradeListView.as_view(), name="FSBid-audit-grade-list"),
    url(r'^options/grade/$', views.FSBidBidAuditGradeOptionsListView.as_view(), name="FSBid-audit-grade-options-list"),
    url(r'^create/grade/$', views.FSBidBidAuditGradeCreateListView.as_view(), name="FSBid-audit-grade-create-list"),
]

urlpatterns += router.urls
