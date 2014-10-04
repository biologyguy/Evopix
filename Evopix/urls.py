from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import public, farm
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', public.index, name='home'),
    url(r'^evp/', include('evp.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^.*', public.not_found, name='404'),
)
