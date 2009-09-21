#
# Test the roles browser view.
#

from zope.component import getMultiAdapter
from base import WorkflowTestCase

from zope.interface import alsoProvides
from Products.GrufSpaces.interface.content import IGroupSpace 
from Globals import PersistentMapping

class TestRolesView(WorkflowTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('testuser', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('nonasciiuser', 'secret', ['Member'], [])
        nonasciiuser = self.portal.portal_membership.getMemberById('nonasciiuser')
        nonasciiuser.setMemberProperties(dict(fullname=u'\xc4\xdc\xdf'.encode('utf-8')))
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', id='folder')
        self.folder = self.portal.folder
        # Make the folder provide the IGroupSpace interface
        self.folder.user_roles = PersistentMapping()
        self.folder.group_roles = PersistentMapping()
        alsoProvides(self.folder, IGroupSpace)
        
    def test_search_by_login_name(self):
        """Make sure we can search by login name on the Roles tab.
        """
        request = self.app.REQUEST
        request.form['search_term'] = 'testuser'
        view = getMultiAdapter((self.folder, request), name='roles')
        results = view.user_search_results()
        self.failUnless(len(results) and results[0].get('id') == 'testuser', msg="Didn't find testuser when I searched by login name.")

    def test_search_with_nonascii_users(self):
        """Make sure we can search with users that have non-ascii-chars in their fullname.
        """
        request = self.app.REQUEST
        request.form['search_term'] = 'nonasciiuser'
        view = getMultiAdapter((self.folder, request), name='roles')
        results = view.role_settings()
        self.failUnless(len(results) and results[0].get('title') == '\xc3\x84\xc3\x9c\xc3\x9f', msg="Umlaute")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRolesView))
    return suite
