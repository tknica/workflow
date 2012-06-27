from django.conf.urls import patterns, include, url

urlpatterns = patterns('workflow.views',

   #url(r'^$','kunden'),
   url(r'^$','print_invoice'),
   url(r'^(?P<customer_id>\d+)/$', 'detail'),
   url(r'^(?P<customer_id>\d+)/results/$', 'results'),
)
