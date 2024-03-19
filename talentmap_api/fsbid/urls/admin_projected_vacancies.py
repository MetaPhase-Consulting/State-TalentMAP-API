from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import admin_projected_vacancies as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^filters/$', views.FSBidAdminProjectedVacancyFiltersView.as_view(), name="admin-projected-vacancies-filters"),
    url(r'^language_offset_options/$', views.FSBidAdminProjectedVacancyLangOffsetOptionsView.as_view(), name="admin-projected-vacancies-lang-offset-options"),
    url(r'^$', views.FSBidAdminProjectedVacancyListView.as_view(), name="admin-projected-vacancies"),
    url(r'^edit/$', views.FSBidAdminProjectedVacancyActionsView.as_view(), name='admin-projected-vacancies-actions'),
    url(r'^edit_language_offsets/$', views.FSBidAdminProjectedVacancyEditLangOffsetsView.as_view(), name='admin-projected-vacancies-edit-lang-offsets'),
    url(r'^edit_capsule_description/$', views.FSBidAdminProjectedVacancyEditCapsuleDescView.as_view(), name='admin-projected-vacancies-edit-capsule-desc'),
    url(r'^language_offsets/$', views.FSBidAdminProjectedVacancyLangOffsetsView.as_view(), name='admin-projected-vacancies-lang-offsets'),
]

urlpatterns += router.urls
