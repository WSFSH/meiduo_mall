from django.conf.urls import url

from apps.index import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
]