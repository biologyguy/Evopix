from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='home'),
    url(r'^evp/', include('evp.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^.*', views.not_found, name='404'),
)
