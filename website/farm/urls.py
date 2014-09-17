from django.conf.urls import *

urlpatterns = patterns('',
                       url(r'^(?P<user_id>\d+)/$', 'farm.views.farm')
                       ,)
