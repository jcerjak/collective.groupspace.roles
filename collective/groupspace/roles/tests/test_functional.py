from base import FunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite
from unittest import TestSuite
from utils import optionflags


def test_suite():
    tests = ['rolespage.txt']
    suite = TestSuite()
    for test in tests:
        suite.addTest(
            FunctionalDocFileSuite(
                test,
                optionflags=optionflags,
                package="collective.groupspace.roles.tests",
                test_class=FunctionalTestCase
            )
        )
    return suite
