from collections import defaultdict
import hashlib
import os
import urllib2
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module


class Suite(object):
    """
    A ``Suite`` represents a self contained javascript testing environment.
    There are external libraries that sometimes need to be pulled in before we
    include the code that needs to be tested.

    .. attribute:: name

        A name for the given test suite

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

    .. attribute:: suites

        List of children suites
    """


    def __init__(self, suite=None, **defaults):
        self.name = ''
        self.remote_urls = []
        self.local_urls = []
        self.tests = []
        self.suites = []
        self.prefix = ''
        self.path = ''
        self.label = ''

        if isinstance(suite, Suite):
            self.__dict__.update(suite.__dict__)
        self.__dict__.update(defaults)

    def _collect(self, attribute):
        items = []
        items.extend(getattr(self, attribute))
        for suite in self.suites:
            items.extend(suite._collect(attribute))
        return items

    def get_remote_urls(self):
        return self._collect('remote_urls')

    def get_local_urls(self):
        return self._collect('local_urls')

    def get_tests(self):
        return self._collect('tests')

    def get_suite_paths(self):
        paths = [self.path]
        for suite in self.suites:
            paths.extend(suite.get_suite_paths())
        return paths

    def test_names(self):
        return [os.path.basename(test) for test in self.tests]

    def test_paths(self):
        return [os.path.join(self.label, test) for test in self.tests]

    def get_hash(self):
        contents = []
        remote_urls = self.get_remote_urls()
        local_urls = self.get_local_urls()
        tests = self.get_tests()
        cache = {}
        # Retrieve remote urls
        for url in remote_urls:
            try:
                content = cache[url]
            except KeyError:
                response = urllib2.urlopen(url)
                content = response.read()
                cache[url] = content
            contents.append(content)

        # Collect local files
        storage = FileSystemStorage(location=settings.STATIC_ROOT)
        for url in local_urls:
            try:
                content = cache[url]
            except KeyError:
                with storage.open(url) as file:
                    content = file.read()
                    contents.append(content)
                    cache[url] = content
            contents.append(content)

        # Collect javascript tests
        prefix = self.prefix
        storage = FileSystemStorage(location=prefix)
        test_paths = [os.path.join(self.path, test) for test in tests]
        for path in test_paths:
            try:
                content = cache[path]
            except KeyError:
                with storage.open(path) as file:
                    content = file.read()
                    contents.append(content)
                    cache[path] = content
            contents.append(content)
        sha = hashlib.sha1("".join(contents)).hexdigest()
        return sha


class SuiteCache(object):
    manifest = 'suite.json'

    def __init__(self):
        self.apps = SortedDict()
        self.cache = defaultdict(dict)
        self._populate()

    def _populate(self):
        for app_name in settings.INSTALLED_APPS:
            mod = import_module(app_name)
            mod_path = os.path.dirname(mod.__file__)
            label = app_name.split('.')[-1]
            tests_path = os.path.join(mod_path, 'tests', 'javascript')
            if os.path.isdir(tests_path):
                self.apps[label] = {
                    "name": app_name,
                    "suite": self.get_app_suites(label, tests_path),
                    'path': tests_path
                }

    def get_app_suites(self, app_name, prefix):
        default = {
            'name': app_name,
            'remote_urls': [],
            'local_urls': [],
            'tests': [],
            'suites': [],
            'label': app_name,
        }
        path = ''
        suite = self._get_suite(app_name, prefix, path, default)
        return suite

    def _get_suite(self, app_name, prefix, path, default):
        """
        :param app_name: The name of the app
        :param prefix: The absolute path to the root of the app's javascript
            suites
        :param path: The path relative to the prefix where the suite is located
        :param default: A dict that provides default values for some of the
            suite's attributes.

        """
        default['suites'] = [] # suites is not inherited
        storage = FileSystemStorage(location=os.path.join(prefix, path))
        suites, tests = storage.listdir('.')
        # If we're implicitly adding tests found within the suite, let's at
        # least sort them in a stable way
        default['tests'] = sorted([os.path.join(path, test) for test in tests if test.endswith('.js')])
        default['name'] = os.path.split(os.path.normpath(path))[-1]
        if storage.exists(self.manifest):
            with storage.open(self.manifest) as json:
                suite = simplejson.loads(json.read())
                default['name'] = suite.pop('name', default['name'])
                default['tests'] = suite.pop('tests', default['tests'])
                default.update(suite)
        for suite_name in suites:
            suite_path = os.path.join(path, suite_name)
            suite = self._get_suite(app_name, prefix, suite_path, default.copy())
            default['suites'].append(suite)
        suite = Suite(**default)
        suite.prefix = prefix
        suite.path = path
        self.cache[app_name][os.path.normpath(path)] = suite
        return suite

    def get_suite(self, app_name, path):
        try:
            return self.cache[app_name][os.path.normpath(path)]
        except KeyError:
            return None

app_suites = SuiteCache()
