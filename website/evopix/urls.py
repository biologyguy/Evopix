from django.conf.urls import *

urlpatterns = patterns('',
                       url(r'^(?P<id>\d+)/$', 'evopix.views.evopic')
                       ,)
