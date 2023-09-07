from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import admin_projected_vacancies as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^filters/$', views.FSBidAdminProjectedVacancyFiltersView.as_view(), name="admin-filters-projected-vacancies"),
    url(r'^$', views.FSBidAdminProjectedVacancyListView.as_view(), name="admin-projected-vacancies"),
]

urlpatterns += router.urls
