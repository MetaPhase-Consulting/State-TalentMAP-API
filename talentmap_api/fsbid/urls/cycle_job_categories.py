from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import cycle_job_categories as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidCycleCategoriesView.as_view(), name="cycle-categories"),
    url(r'^job_categories/$', views.FSBidCycleJobCategoriesView.as_view(), name="cycle-job-categories"),
    url(r'^job_categories/edit$', views.FSBidCycleJobCategoriesActionView.as_view(), name="edit-cycle-job-categories"),
]

urlpatterns += router.urls
