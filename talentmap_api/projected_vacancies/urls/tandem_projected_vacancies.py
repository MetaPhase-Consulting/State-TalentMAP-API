from django.conf.urls import url
from rest_framework import routers

from talentmap_api.projected_vacancies.views import tandem_projected_vacancy as views

from talentmap_api.common.urls import get_list

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/$', views.ProjectedVacancyFavoriteTandemListView.as_view(), name='view-tandem-favorite-projected-vacancies'),
    url(r'^favorites/ids/$', views.ProjectedVacancyFavoriteTandemIdsListView.as_view(), name='view-tandem-favorite-projected-vacancies-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.ProjectedVacancyFavoriteTandemActionView.as_view(), name='projected_vacancies-ProjectedVacancyFavorite-tandem-favorite'),
]

urlpatterns += router.urls
