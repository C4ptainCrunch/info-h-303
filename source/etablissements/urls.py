from django.conf.urls import patterns, url
from .views import list_etablissements

urlpatterns = patterns(
    '',
    url(r'^$', list_etablissements, name='list_etablissements'),
)
