##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: public.py,v 1.2 2004/08/18 15:23:01 godchap Exp $
"""
try:
    from Products.CompositePack.ClassGen import registerType
except ImportError:
    from Products.Archetypes.public import registerType

try:
    from Products.LinguaPlone.public import BaseContent
except ImportError:
    from Products.Archetypes.public import BaseContent

