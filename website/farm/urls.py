from django.conf.urls import *

urlpatterns = patterns('',
                       url(r'^(?P<id>\d+)/$', 'farm.views.farm')
                       ,)
