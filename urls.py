#from django.conf.urls import patterns, include, url

from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
   url(r'^print_invoice/','workflow.views.print_invoice'),
   url(r'^remove_pos_from_invoice/','workflow.views.remove_pos_from_invoice'),
   url(r'', include(admin.site.urls)),
)
