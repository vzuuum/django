from django.conf.urls.defaults import url, patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.test.javascript.views import JavascriptTestOverview, \
    JavascriptTestRunner, static_path


urlpatterns = patterns('',
    url('^test/(?P<path>.*)$', 'django.views.static.serve', {'document_root': static_path}, name='javascript-static'),
    url('^$', JavascriptTestOverview.as_view(), name='javascript-test-overview'),
    url('^(?P<label>[\w]+)/(?P<path>.*)$', JavascriptTestRunner.as_view(), name='javascript-test-runner'),
) + staticfiles_urlpatterns()
