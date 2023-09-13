from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import job_categories as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^$', views.FSBidJobCategoriesListView.as_view(), name='FSBid-job-categories-list'),
    url(r'^skills/$', views.FSBidJobCategorySkillsListView.as_view(), name='FSBid-job-category-skills-list'),
]

urlpatterns += router.urls
