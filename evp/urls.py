from django.conf.urls import patterns, url

from evp import views

urlpatterns = patterns('',
    url(r'^$', views.welcome, name='welcome'),
)