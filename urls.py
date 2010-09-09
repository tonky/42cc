from django.conf.urls.defaults import *
from settings import STATIC_ROOT
from bio.models import Log

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'bio.views.index'),
    (r'^edit/$', 'bio.views.edit'),
    (r'^save/$', 'bio.views.save'),
    (r'^save_ajax/$', 'bio.views.save_ajax'),
    (r'^login/$', 'django.contrib.auth.views.login',
                  {'template_name': 'login.html'}),
    (r'^logout/$', 'bio.views.logoff'),
    (r'^first10/$', 'django.views.generic.list_detail.object_list',
                    {'template_name': 'ten_requests.html',
                     'queryset': Log.objects.all()[:10]}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': STATIC_ROOT}),
)
