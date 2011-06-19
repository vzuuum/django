from django.conf.urls.defaults import url, patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.test.javascript.views import JavascriptTestOverview, \
    JavascriptTest, static_path


urlpatterns =  staticfiles_urlpatterns() + patterns('',
    url('^test/(?P<path>.*)$', 'django.views.static.serve', {'document_root': static_path}, name='javascript-static'),
    url('^$', JavascriptTestOverview.as_view(), name='javascript-test-overview'),
    url('^(?P<label>[\w]+)/(?P<path>.*)$', JavascriptTest.as_view(), name='javascript-test-runner'),
)

