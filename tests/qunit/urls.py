import os
from django.conf.urls.defaults import *

document_root = os.path.join(os.path.dirname(__file__), 'static')

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': document_root}),
    url('^', include('django_qunit.urls'))
)
