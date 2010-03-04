from django.conf.urls.defaults import *


urlpatterns = patterns('cache_plot.views',
    # Example:
    # (r'^finderweb/', include('finderweb.foo.urls')),

    # Uncomment this for admin:
    (r'^$', 'pages'),
    (r'pages/$', 'pages'),
    (r'tables/$', 'tables'),
    (r'stats/$', 'stats'),

)

