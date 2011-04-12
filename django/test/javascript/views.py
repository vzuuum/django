from __future__ import with_statement

import hashlib
import os
import urllib2
from time import sleep
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.utils import simplejson, datastructures
from django.utils.importlib import import_module
from django.views import generic, static
from django.core.urlresolvers import reverse
from django.test.javascript.suite import app_suites

thisdir = os.path.dirname(__file__)
static_path = os.path.join(thisdir, 'static')
templates_path = os.path.join(thisdir, 'templates')


class JavascriptTestOverview(generic.TemplateView):
    template_name = 'javascript/overview.html'

    def __init__(self, *args, **kwargs):
        super(JavascriptTestOverview, self).__init__(*args, **kwargs)
        self.app_suites = app_suites

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JavascriptTestOverview, self).get_context_data(**kwargs)
        context.update({
            'app_suites': self.app_suites,
        })
        return context


class JavascriptTest(generic.TemplateView):
    template_name = 'javascript/runner.html'

    def __init__(self, *args, **kwargs):
        super(JavascriptTest, self).__init__(*args, **kwargs)
        self.app_suites = app_suites

    def get(self, request, label, path=None, *args, **kwargs):
        suite_path = path
        if path.endswith('.js'):
            suite_path = os.path.dirname(path)
        suite = self.app_suites.get_suite(label, suite_path)
        if suite is None:
            raise Http404("No test suite found with label '%s'" % label)
        full_path = os.path.join(suite.prefix, path)
        if os.path.isfile(full_path):
            dir, filename = os.path.split(full_path)
            return static.serve(request, path=filename, document_root=dir)
        elif not os.path.isdir(full_path):
            raise Http404("No test suite found with label '%s'" % label)
        context = self.get_context_data(request, suite, *args, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, request, suite, **kwargs):
        context = super(JavascriptTest, self).get_context_data(**kwargs)
        context.update({
            'suite': suite,
            'path': request.path,
        })
        return context
