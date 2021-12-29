from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import agenda as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^agenda_items/$', views.AgendaItemView.as_view(), name="agenda-agenda-items"),
    url(r'^agenda_items/(?P<client_id>[0-9]+)/export/$', views.AgendaItemCSVView.as_view(), name="agenda-export-agenda-items"),
]

urlpatterns += router.urls
