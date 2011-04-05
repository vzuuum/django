from __future__ import with_statement

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.utils import simplejson, datastructures
from django.utils.importlib import import_module
from django.views import generic, static
from django.core.urlresolvers import reverse

thisdir = os.path.dirname(__file__)
static_path = os.path.join(thisdir, 'static')
templates_path = os.path.join(thisdir, 'templates')



class Suite(object):
    """
    A ``Suite`` represents a self contained javascript testing environment.
    There are external libraries that sometimes need to be pulled in before we
    include the code that needs to be tested.

    .. attribute:: name

        A name for the given test suite

    .. attribute:: tests_path

        The path to the suite.

    .. attribute:: remote_urls

        URLs to external libraries, e.g. jQuery, Mootools, etc.

    .. attribute:: local_urls

        URLs to the code being tested. URLs are relative the to the STATIC_URL
        setting.

    .. attribute:: tests

        Explicit list of tests to be included under this suite.  Overrides the
        default behavior of including all .js files within the suite's
        directory.  Useful for explicitly listing the order of tests, omitting
        certains tests, or including tests from other nested suites.

    """
    name = ''
    tests_path = ''
    remote_urls = []
    local_urls = []

    def __init__(self, name, tests_path, remote_urls=None, local_urls=None):
        self.name = name
        self.tests_path = tests_path
        if local_urls is not None:
            self.local_urls = local_urls
        if remote_urls is not None:
            self.remote_urls = remote_urls


def get_suites():
    suites = datastructures.SortedDict()
    for app_name in settings.INSTALLED_APPS:
        mod = import_module(app_name)
        mod_path = os.path.dirname(mod.__file__)
        label = app_name.split('.')[-1]
        tests_path = os.path.join(mod_path, 'tests', 'javascript')
        if os.path.isdir(tests_path):
            suites[label] = {
                "local_urls": [],
                "remote_urls": [],
                "name": app_name,
                "test": ""
            }
    return suites

class JavascriptTestOverview(generic.TemplateView):
    manifest = 'suite.json'
    template_name = 'javascript/overview.html'

    def __init__(self, *args, **kwargs):
        super(JavascriptTestOverview, self).__init__(*args, **kwargs)
        self.suites = get_suites()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JavascriptTestOverview, self).get_context_data(**kwargs)
        context.update({
            'suites': self.suites,
            'linkbase': reverse('javascript-test-overview'),
        })
        return context


class JavascriptTestRunner(generic.TemplateView):
    manifest = 'suite.json'
    template_name = 'javascript/runner.html'

    def get(self, request, label=None, path=None, *args, **kwargs):
        """

        """
        if label is not None:
            suite = self.suites.get(label)
            if suite is None:
                raise Http404("No test suite found with label '%s'" % label)
            full_path = os.path.join(suite['tests_path'], path)
            if os.path.isfile(full_path):
                dir, filename = os.path.split(full_path)
                return static.serve(request, path=filename, document_root=dir)
            context = self.get_context_data(suite, full_path, *args, **kwargs)
        else:
            context = self.get_context_data(*args, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, suite=None, full_path=None, **kwargs):
        context = super(JavascriptTestRunner, self).get_context_data(**kwargs)
        context.update({
            'suites': self.suites,
            'linkbase': reverse('javascript-test-overview'),
        })
        if full_path:
            storage = FileSystemStorage(location=full_path)
            # load suite.json if present
            if storage.exists(self.manifest):
                with storage.open(self.manifest) as json:
                    suite.update(simplejson.loads(json.read()))

            directories, files = storage.listdir('.')
            context.update({
                'suite': suite,
                'subsuites': directories,
                'files': [file for file in files if file.endswith('js')],
            })
        return context
