from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import public, farm
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', public.index, name='home'),
    #url(r'^evp/', include('evp.urls')),
    url(r'^home/?$', farm.welcome, name='welcome'),
    url(r'^farm/?$', farm.farm, name='farm'),
    url(r'^bob/?$', farm.bob, name='bob'),
    #url(r'^move/{0,1}$', farm.move, name='move'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^404$', public.not_found, name='404'),
    #AJAX views
    url(r'^populate_map/?$', farm.populate_map, name='populate_map'),
    url(r'^user_login/?$', public.user_login, name='login'),
    url(r'^.*', public.not_found, name='not_found'),
)
