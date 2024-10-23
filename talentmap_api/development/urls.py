from django.urls import include, path
from . import views


urlpatterns = [
	path(r'^$', views.devIndex, name='devIndex'),
]
