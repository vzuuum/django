"""
Javascript Testing Framework
============================


Setup
-----

Django uses Qunit for javascript testing and has a framework for developers to
use when integrating all their javascript unit tests.

Javascript tests should be placed under the following file structure::

    <app>/tests/javascript/

Under that directory should exist all the javascript test files.  However,
adding test files is pretty pointless unless you indicate what javascript needs
to be tested.  To provide information about what you are testing, you should
add a ``suites.json`` manifest file that contains some meta data about the
tests that are going to be run.

The following are properties of the manifest file ``suites.json``:

``name``

    A name for the given test suite

``remote_urls``

    URLs to external libraries, e.g. jQuery, Mootools, etc.

``local_urls``

    URLs to the code being tested. URLs are relative the to the STATIC_URL
    setting.

``tests``

    Explicit list of tests to be included under this suite.  Overrides the
    default behavior of including all .js files within the suite's
    directory.  Useful for explicitly listing the order of tests, omitting
    certains tests, or including tests from other nested suites.

An example ``suites.json`` file might look like this::

    {
        "name": "My Super Cool Javascript Test Suite",
        "remote_urls": [
          "http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"
        ],
        "local_urls": [
            "admin/js/dateparse.js",
            "admin/js/timeparse.js",
        ],
        "tests": [
            "dateparse_tests.js",
            "timeparse_tests.js"
        ]
    }


Nested Suites
~~~~~~~~~~~~~

Sometimes it's beneficial to break up your tests into different chunks for a few
reasons including organizational purposes or because there are two or more
versions of code that will trample each other's namespace.

To keep this DRY and organized, you can include nested suites in your javascript
test directory.  Any directory found is interpreted as another suite that
inherits it's parent ``suites.json`` manifest unless the suite provides its own.
A child suite manifest does not need to provide all the fields and will use its
parent's manifest for fields that are not provided.  However, the ``tests``
field is not inherited because the lack of a ``suites.json`` file means that
you want to use the parent manifest, but test the files within the child suite's
directory.

<DDN: Should we dump the implicit behavior and insist on including a suites.json
    for every child test suite?>


Javascript Testing
------------------

Once tests are written, Django provides a managment command to start a simple
webserver that collect the necessary static files and runs the javascript suites
in your browser. On the command line, simply type::

    django-admin.py jstest

Overview
~~~~~~~~

The overview page is a display of all the apps found within ``INSTALLED_APPS``
that have javascript tests.  For each app it displays whether it has passed,
failed, or needs to be run.  It also displays when it last run and how long it
took (if applicable).

On the overview page, tests can be run all at once or one by one.  Whenever the
tests are run, the overview page instantiates a hidden iframe pointing to a test
suite runner.  Once the runner completes, the javascript attaches the results on
the top window and updates the app's test result information.  We use a
persistent store to save the client-side test results for an app, based on the
hash of all the tests and dependencies.  This ensures that any change in the
external libraries, internal javascript code, or the tests themselves will
require the tests to be run again.  However, viewing the results for each
individual test can only be displayed by navigating to the suite's test runner
page.

Test Runner
~~~~~~~~~~~

When you click on the app link on the overview page, the browser will take you
to the root suite test runner.  Near the top there is a navigation menu that
lists all the child suites and a link labeled "..", which points to either the
overview page or a parent suite if you have navigated to a child suite.
Each test runner page shows the individual tests defined within your suite.
All passing tests are highlighted in green and all failing tests in red.

"""
