from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import public, farm
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', public.index, name='home'),
    #url(r'^evp/', include('evp.urls')),
    url(r'^home$', farm.welcome, name='farm'),
    url(r'^bob$', farm.bob, name='bob'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^404$', public.not_found, name='404'),
    url(r'^.*', public.not_found, name='not_found'),
)
