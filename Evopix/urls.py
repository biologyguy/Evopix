from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import public, farm
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', public.index, name='home'),
    #url(r'^evp/', include('evp.urls')),
    url(r'^home/{0,1}$', farm.welcome, name='welcome'),
    url(r'^farm/{0,1}$', farm.farm, name='farm'),
    url(r'^bob/{0,1}$', farm.bob, name='bob'),
    url(r'^mutate/{0,1}$', farm.mutate, name='mutate'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^404$', public.not_found, name='404'),
    url(r'^.*', public.not_found, name='not_found'),
)
