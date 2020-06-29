from django.conf.urls import url
from rest_framework import routers

from talentmap_api.available_positions.views import tandem_available_position as views

from talentmap_api.common.urls import patch_update

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/export/$', views.FavoritesTandemCSVView.as_view(), name='export-all-favorites'),
    url(r'^favorites/$', views.AvailablePositionFavoriteTandemListView.as_view(), name='view-favorite-available-positions'),
    url(r'^favorites/ids/$', views.AvailablePositionFavoriteTandemIdsListView.as_view(), name='view-favorite-available-positions-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.AvailablePositionFavoriteTandemActionView.as_view(), name='available_positions-AvailablePositionFavorite-favorite'),
]

urlpatterns += router.urls
