from types import StringTypes

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from groupspace.roles import rolesMessageFactory as _

from Acquisition import aq_inner

from plone.memoize.compress import xhtml_compress
from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.app.portlets.cache import render_cachekey

from zope.component import queryAdapter
from plone.portlets.interfaces import IPortletContext

class IMyGroupsPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMyGroupsPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "My Groups"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('mygroupsportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data())

    def allowed_groupspaces(self):
        return self._data()

    @memoize
    def _data(self):
        context = aq_inner(self.context)

        catalog = getToolByName(context, 'portal_catalog')

        allowed = self._getUserAndGroupIds()
        if allowed == []:
            return []
            
        return catalog(portal_type='GroupSpace',
                       allowedLocalUsersAndGroups=allowed,
                       sort_on='sortable_title')


    def _getUserAndGroupIds(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
            return []
        member = membership.getAuthenticatedMember()
        if not member:
            return []
        memberId = member.getId()
        if memberId is None:
            # Basic users such as the special Anonymous users have no
            # id, but we can use their username instead.
            try:
                memberId = member.getUserName()
            except AttributeError:
                pass
        if not memberId:
            return []
        allowed = ['user:%s' % memberId]
        groups = member.getGroups()
        for group in groups:
            if type(group) in StringTypes:
                allowed.append('group:%s' % group)
        return allowed
        
# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMyGroupsPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMyGroupsPortlet)
