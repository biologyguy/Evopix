from django.conf.urls import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'views.index'),
                       (r'^farm/', include('farm.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )
