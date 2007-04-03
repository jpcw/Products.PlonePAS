##############################################################################
#
# PlonePAS - Adapt PluggableAuthService for use in Plone
# Copyright (C) 2005 Enfold Systems, Kapil Thangavelu, et al
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

This script runs CMFPlone tests with our PAS user folder instead of the
standard GRUF in order to flush out changes that need to be made to Plone in
order to use PAS. Usage:

% python seeWhatBreaks.py testFoo testBar

The arguments are module names in CMFPlone/tests. They are imported (as opposed
to execfile'd) so you don't need the '.py' extension. If no args are given, all
tests will be run, and a summary of broken test modules will be output.

$Id: seeWhatBreaks.py 18307 2006-01-22 17:28:37Z alecm $
"""

# framework is copied over from CMFPlone/tests
import os, sys
tests = sys.argv[1:]
sys.argv = sys.argv[:1]

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# now run our tests
import unittest
TestRunner = unittest.TextTestRunner
g = globals()

if tests:
    # if we are given args, only run those tests; build one big suite and
    #  return the usual verbose output

    suite = unittest.TestSuite()
    for test in tests:
        m = __import__('Products.CMFPlone.tests.'+test,g,g,test)
        if hasattr(m, 'test_suite'):
            suite.addTest(m.test_suite())
    def runtests():
        TestRunner().run(suite)

elif not tests:
    # if no args, run all tests but only give limited output

    # first list all available CMFPlone test modules
    from Products.CMFCore import utils
    CMFPLONE_TESTS = os.sep.join(('CMFPlone','tests'))
    CMFPLONE_TESTS = utils.expandpath(CMFPLONE_TESTS)
    tests = os.listdir(CMFPLONE_TESTS)
    tests = [n[:-3] for n in tests if n.startswith('test') \
                                  and n.endswith('.py')]

    # then run a test suite for each one and capture the output
    def runtests():
        # set up a dummy stream to swallow output
        from StringIO import StringIO
        devnull = StringIO()

        # output a header
        print
        print "Module                        Errors  Failures"
        print "=" * 79
        template = "%(module)s  %(errors)s    %(failures)s"
        data = {}
        totalerrors = totalfailures = 0

        # run our tests
        for test in tests:
            m = __import__('Products.CMFPlone.tests.'+test,g,g,test)
            if hasattr(m, 'test_suite'):
                suite = unittest.TestSuite()
                suite.addTest(m.test_suite())
            else:
                continue
            results = TestRunner(devnull,False,0).run(suite)

            data['module'] = test[:28].ljust(28)

            numerrors = len(results.errors)
            totalerrors += numerrors
            data['errors'] = str(numerrors).rjust(4)

            numfailures = len(results.failures)
            totalfailures += numfailures
            data['failures'] = str(numfailures).rjust(4)

            if numerrors + numfailures > 0:
                # don't talk about working tests
                print template % data

        totals = (str(totalerrors).rjust(4), str(totalfailures).rjust(4))
        print "-" * 79
        print "TOTAL                         %s    %s" % totals


# ... and run them!
if __name__ == '__main__':
    runtests()
