from zope.app import zapi
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.Archetypes.utils import shasattr
from Products.CompositePack.interfaces import ICompositeTool
from Products.CompositePack.Extensions.Install import toolWrapper

nodeTypeMap = {'layouts':'CompositePack Layout Container',
               'layout':'CompositePack Layout',
               'viewlet':'CompositePack Viewlet',
               'viewlets':'CompositePack Viewlet Container',
               'classes':'Slot Class Folder',
               'class':'Slot Class',
    }
containers = ['layouts','viewlets','classes']


class CompositeToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """
    Node im- and exporter for composite tool.
    """
    __used_for__ = ICompositeTool

    name = 'composite_tool'

    def _exportNode(self):
        """
        Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractCompositeConfiguration())
        self._logger.info("Composite settings exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()

        self._initObjects(node)
        self._logger.info("Composite settings imported.")
        
    def _purgeObjects(self):
        """ Keep the following folders:
              -  CompositePack Layout Container
              -  CompositePack Viewlet Container
              -  Slot Class Folder
            but delete all child object inside those folders
        """
        tool = self.context
        for id in tool.objectIds():
            ids =  tool['id'].objectIds()
            tool['id'].delObjects(ids)

    def _extractCompositeConfiguration(self):
        """
        Generate the compositetool.xml from the current configuration.
        """
        fragment = self._doc.createDocumentFragment()
        tool = self.context

        # Lets start with the composites.
        compositesElement = self._doc.createElement('composites')
        compositesElement.setAttribute('name', 'composites')
        for composite in tool.getRegisteredComposites():
            child = self._doc.createElement('composite')
            child.setAttribute('name', composite)
            compositeElement = compositesElement.appendChild(child)

            layoutsForType = tool.getRegisteredLayoutsForType(composite)
            layoutsForType = [l.getId() for l in layoutsForType]
            for layout in layoutsForType:
                child = self._doc.createElement('c_layout')
                child.setAttribute('name', layout)
                default_layout = tool.getDefaultLayoutForType(composite).getId()
                if default_layout == layout and len(layoutsForType) > 1:
                    child.setAttribute('default', 'True')
                compositeElement.appendChild(child)
        fragment.appendChild(compositesElement)

        # Now for the composables.
        composablesElement = self._doc.createElement('composables')
        composablesElement.setAttribute('name', 'composites')
        for composable in tool.getRegisteredComposables():
            child = self._doc.createElement('composable')
            child.setAttribute('name', composable)
            composableElement = composablesElement.appendChild(child)

            viewletsForType = tool.getRegisteredViewletsForType(composable)
            viewletsForType = [v.getId() for v in viewletsForType]
            for viewlet in viewletsForType:
                child = self._doc.createElement('c_viewlet')
                child.setAttribute('name', viewlet)
                default_viewlet = tool.getDefaultViewletForType(composable).getId()
                if default_viewlet == viewlet and len(viewletsForType) > 1:
                    child.setAttribute('default', 'True')
                composableElement.appendChild(child)
        fragment.appendChild(composablesElement)

        # Let's add some viewlet!
        viewletsElement = self._doc.createElement('viewlets')
        viewletsElement.setAttribute('name', 'viewlets')
        for viewlet in tool.getAllViewlets():
            child = self._doc.createElement('viewlet')
            child.setAttribute('name', viewlet.getId())
            child.setAttribute('title', viewlet.Title())
            child.setAttribute('skin_method', viewlet.getSkinMethod())
            viewletsElement.appendChild(child)
        fragment.appendChild(viewletsElement)

        # Let's add some layouts!
        layoutsElement = self._doc.createElement('layouts')
        layoutsElement.setAttribute('name', 'layouts')
        for layout in tool.getAllLayouts():
            child = self._doc.createElement('layout')
            child.setAttribute('name', layout.getId())
            child.setAttribute('title', layout.Title())
            child.setAttribute('skin_method', layout.getSkinMethod())
            layoutsElement.appendChild(child)
        fragment.appendChild(layoutsElement)

        return fragment

    def _configureComposables(self, node):
        """ Configure the mapping between content types and layouts
        """
        import pdb; pdb.set_trace()
        wtool = toolWrapper(self.context)
        comp_items = list()
        # Register composables first
        for composable in _filterNodes(node.childNodes):
            comp_items.append(composable.getAttribute('name'))
        wtool.registerAsComposable(comp_items)
        for composable in _filterNodes(node.childNodes):
            composable_id = composable.getAttribute('name')
            default_viewlet = ''
            c_viewlets = list()
            # Now register viewlets for each composable
            for c_viewlet in _filterNodes(composable.childNodes):
                c_viewlet_id = c_viewlet.getAttribute('name')
                c_viewlets.append(c_viewlet_id)
                if c_viewlet.hasAttribute('default'):
                    default_viewlet = c_viewlet_id
            if default_viewlet == '':
                if c_viewlets == []:
                    raise ValueError
                default_viewlet = c_viewlets[0]

            wtool.setViewletsForType(composable_id, c_viewlets, default_viewlet)

    def _configureComposites(self, node):
        """ Configure the mapping between content types and layouts
        """
        # import pdb; pdb.set_trace()

    def _configureLayouts(self, node):
        """ Configure the layouts
        """

    def _configureViewlets(self, node):
        """ Configure the Viewlets
        """
        # import pdb; pdb.set_trace()

    def _initObjects(self, node):
        """ Import subobjects from the DOM tree.
            Directly under a compositetool we are allowed to create:
                -  CompositePack Layout Container
                -  CompositePack Viewlet Container
                -  Slot Class Folder
            Within each container only one type of object can be created
                -  CompositePack Layout
                -  CompositePack Viewlet
                -  Slot Class
                
            Base on the nodeName of the DOM we create the corresponding type of object.
            
        """

        first_level_nodes = {
            "layouts"     : self._configureLayouts,
            "viewlets"    : self._configureViewlets,
            "composites"  : self._configureComposites,
            "composables" : self._configureComposables,
        }

        for child in _filterNodes(node.childNodes):
            if child.nodeName not in first_level_nodes.keys():
                continue
            first_level_nodes.get(child.nodeName)(child)

def _filterNodes(nodes):
    """
    return a list of nodes with textnodes filtered out.
    """
    return [node for node in nodes if not shasattr(node, 'data')]


def importCompositeTool(context):
    """ Import composite tool properties.
    """
    site = context.getSite()
    logger = context.getLogger('composite tool properties')
    tool = getToolByName(site, 'composite_tool')

    body = context.readDataFile('compositetool.xml')
    if body is None:
        logger.info('Composite tool: Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Composite tool: Import adapter misssing.')
        return

    importer.body = body

    importObjects(tool, '', context)
    logger.info('Composite tool imported.')

def exportCompositeTool(context):
    """ Export composite tool properties.
    """

    site = context.getSite()
    logger = context.getLogger('composite tool properties')
    tool = getToolByName(site, 'composite_tool', None)
    if tool is None:
        logger.info('Composite tool: Nothing to export.')
        return

    exportObjects(tool, '', context)
    logger.info('Composite tool properties exported.')

