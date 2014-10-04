from django.conf.urls import patterns, url

from views import farm, public

urlpatterns = patterns('',
    url(r'^$', farm.welcome, name='welcome'),

)