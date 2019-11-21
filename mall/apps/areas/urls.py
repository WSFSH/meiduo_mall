from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^areas/$', views.AreasView.as_view(), name='areas'),
    url(r'^address/create/$', views.CreateAddressView.as_view(), name='createaddress'),
    url(r'^address/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name='updateaddress'),
    url(r'^address/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='defaultaddress'),
    url(r'^address/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name='titleaddress'),

]