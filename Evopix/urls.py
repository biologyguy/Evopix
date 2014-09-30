from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^home/', 'templates.welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'Evopix.views.home', name='home'),
)
