from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^areas/$', views.AreasView.as_view(), name='areas'),
    url(r'^address/create/$', views.CreateAddressView.as_view(), name='createaddress'),
]