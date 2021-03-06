# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################

"""
$Id$
"""

import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from Products.CompositePack.exceptions import CompositePackError
from Products.CompositePack.testing import INTEGRATION_TESTING


class TestLayoutRegistry(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.composite_tool = getToolByName(self.portal, 'composite_tool')

        self.TEST_TYPE = 'File'
        self.TEST_TYPE_2 = 'Event'
        self.TEST_TYPES = (self.TEST_TYPE, self.TEST_TYPE_2)
        ct = self.composite_tool
        ct.unregisterAsComposite(self.TEST_TYPE)
        ct.unregisterAsComposite(self.TEST_TYPE_2)

    def testRegisterType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        self.failUnless(ct.isComposite(self.TEST_TYPE))
        self.failUnless(self.TEST_TYPE in ct.getRegisteredComposites())

    def testUnregisterType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        ct.unregisterAsComposite(self.TEST_TYPE)
        self.failIf(ct.isComposite(self.TEST_TYPE))

    def testRegisterTypes(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPES)
        for test_type in self.TEST_TYPES:
            self.failUnless(ct.isComposite(test_type))
            self.failUnless(test_type in ct.getRegisteredComposites())

    def testUnregisterTypes(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPES)
        ct.unregisterAsComposite(self.TEST_TYPES)
        for test_type in self.TEST_TYPES:
            self.failIf(ct.isComposite(test_type))

    def testRegisterTwice(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        self.assertRaises(CompositePackError, ct.registerAsComposite, self.TEST_TYPE)

    def testRegisterLayout(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        self.assertEquals(layout, ct.getLayoutById('test_layout'))

    def testUnregisterLayout(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        ct.unregisterLayout('test_layout')
        self.assertEquals(None, ct.getLayoutById('test_layout'))
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        ct.unregisterLayout('test_layout')
        self.failIf('test_layout' in [layout.getId() for layout in ct.getRegisteredLayoutsForType(self.TEST_TYPE)])

    def testRegisterLayoutForType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        self.failUnless(layout in ct.getRegisteredLayoutsForType(self.TEST_TYPE))
        #it can be registered twice !
        layout.registerForType(self.TEST_TYPE)
        self.failUnless(layout.isRegisteredForType(self.TEST_TYPE))
        self.failIf(layout.isDefaultForType(self.TEST_TYPE))
        self.failUnless(layout in ct.getRegisteredLayoutsForType(self.TEST_TYPE))

    def testUnregisterLayoutForType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        layout.unregisterForType(self.TEST_TYPE)
        self.failIf(layout.isRegisteredForType(self.TEST_TYPE))
        self.failIf(layout in ct.getRegisteredLayoutsForType(self.TEST_TYPE))

    def testRegisterDefaultLayoutForType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        layout.setDefaultForType(self.TEST_TYPE)
        self.assertEquals(layout, ct.getDefaultLayoutForType(self.TEST_TYPE))
        self.failUnless(layout.isDefaultForType(self.TEST_TYPE))

    def testUnRegisterDefaultLayoutForType(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        layout.setDefaultForType(self.TEST_TYPE)
        self.assertRaises(CompositePackError, layout.unregisterForType, self.TEST_TYPE)

    def testClearDefaultLayout(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        layout.setDefaultForType(self.TEST_TYPE)
        layout.clearDefaultForType(self.TEST_TYPE)
        self.assertEquals(ct.getDefaultLayoutForType(self.TEST_TYPE).getId(),
                          ct.getDefaultLayout())
        self.failUnless(ct.noDefaultLayoutForType(self.TEST_TYPE))

    def testForceUnRegisterDefaultLayout(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        layout.registerForType(self.TEST_TYPE)
        layout.setDefaultForType(self.TEST_TYPE)
        layout.unregisterForType(self.TEST_TYPE, force=True)
        self.assertEquals(ct.getDefaultLayoutForType(self.TEST_TYPE).getId(),
                          ct.getDefaultLayout())

    def testDefaultLayoutNotRegistered(self):
        ct = self.composite_tool
        ct.registerAsComposite(self.TEST_TYPE)
        self.assertEquals(ct.getDefaultLayoutForType(self.TEST_TYPE).getId(),
                          ct.getDefaultLayout())

    def testDefaultLayoutNotRegisteredUsesToolDefault(self):
        ct = self.composite_tool
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        ct.setDefaultLayout('test_layout')
        ct.registerAsComposite(self.TEST_TYPE)
        self.assertEquals(ct.getDefaultLayoutForType(self.TEST_TYPE),
                          layout)

    def testLayoutsForTypeNotRegisteredReturnAll(self):
        ct = self.composite_tool
        layouts = ct.layouts.objectValues()
        self.assertEquals(ct.getRegisteredLayoutsForType(self.TEST_TYPE),
                          layouts)
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        ct.registerLayoutForType(layout, self.TEST_TYPE)
        self.assertEquals(ct.getRegisteredLayoutsForType(self.TEST_TYPE),
                          [layout])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
