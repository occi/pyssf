#
# Copyright (C) 2010-2011 Platform Computing
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
Module to test the parser.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Access to a protected' pyling check (this is a test)
# pylint: disable=C0103,R0904,W0212

from occi.core_model import Action, Kind, Resource, Link
from occi.protocol import occi_parser as parser
from occi.registry import NonePersistentRegistry
import unittest


class TestParser(unittest.TestCase):
    '''
    Test for the parser.
    '''

    start_action = Action('http://schemas.ogf.org/occi/infrastructure#',
                          'start')
    compute = Kind('http://schemas.ogf.org/occi/infrastructure#',
                       'compute', title='A OCCI compute...',
                       attributes={'occi.compute.cores': '',
                                   'occi.compute.state': 'immutable',
                                   'occi.compute.memory': 'required'},
                   related=[Resource.kind],
                   actions=[start_action])
    network_link = Kind('http://schemas.ogf.org/occi/infrastructure#',
                        'networkinterface',
                        related=[Link.kind]
                        )

    source = Resource('/1', compute, [])
    target = Resource('/2', compute, [])
    link1 = Link('/link/1', network_link, [], source, target)
    link2 = Link(None, network_link, [], source, target)

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.add_resource(self.source.identifier, self.source)
        self.registry.add_resource(self.target.identifier, self.target)

        self.registry.set_backend(self.start_action, None)
        self.registry.set_backend(self.compute, None)
        self.registry.set_backend(self.network_link, None)

        self.link1.attributes = {'foo': 'bar'}

    def tearDown(self):
        for item in self.registry.get_categories():
            self.registry.delete_mixin(item)

    #==========================================================================
    # Success
    #==========================================================================

    def test_get_category_for_success(self):
        '''
        Tests if a mixin can be created.
        '''

        # disabling 'Method could be func' pylint check (pyunit fault :-))
        # pylint: disable=R0201

        # mixin check...
        tmp = 'foo; scheme="http://example.com#"; location="/foo_bar/"'
        parser.get_category(tmp, self.registry.get_categories(), is_mixin=True)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_get_category_for_failure(self):
        '''
        Test with faulty category.
        '''
        self.assertRaises(AttributeError, parser.get_category, 'some crap',
                          self.registry.get_categories())
        self.assertRaises(AttributeError, parser.get_category,
                          'foo; scheme="bar"',
                          self.registry.get_categories())

        # mixin with msg location check...
        tmp = 'foo; scheme="http://example.com#"'
        self.assertRaises(AttributeError, parser.get_category, tmp,
                          self.registry.get_categories(), True)

        # mixin with faulty location check...
        tmp = 'foo; scheme="http://example.com#"; location="sdf"'
        self.assertRaises(AttributeError, parser.get_category, tmp,
                          self.registry.get_categories(), True)

    def test_get_link_for_failure(self):
        '''
        Test with msg category.
        '''
        # no valid string...
        self.assertRaises(AttributeError, parser.get_link, 'some crap', None,
                          self.registry.get_categories())

        # no target...
        link_string = parser.get_link_str(self.link1)
        self.registry.delete_resource(self.target.identifier)
        self.assertRaises(AttributeError, parser.get_link, link_string, None,
                          self.registry)

    def test_get_attributes_for_failure(self):
        '''
        Verifies the parsing of attributes.
        '''
        self.assertRaises(AttributeError, parser.get_attributes, 'bla blub')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_get_category_for_sanity(self):
        '''
        Simple sanity check...
        '''
        res = parser.get_category(parser.get_category_str(self.compute),
                          self.registry.get_categories())
        self.assertEqual(res, self.compute)

    def test_get_link_for_sanity(self):
        '''
        Verifies that source and target are set...
        '''
        link_string = parser.get_link_str(self.link1)
        link = parser.get_link(link_string, self.source, self.registry)
        self.assertEquals(link.kind, self.network_link)
        self.assertEquals(link.source, self.source)
        self.assertEquals(link.target, self.target)
        # 4 = 1 attr + core.id + core.src + core.target
        self.assertTrue(len(link.attributes) == 4)

        # identifier checks...
        link_string = parser.get_link_str(self.link1)
        link = parser.get_link(link_string, self.source, self.registry)
        self.assertEquals(link.identifier, '/link/1')

        tmp = link_string.split('; ')
        tmp.pop(2)
        link_string = '; '.join(tmp)
        link = parser.get_link(link_string, self.source, self.registry)
        self.assertEquals(link.identifier, None)

    def test_strip_all_for_sanity(self):
        '''
        Tests if information get's stripped correctly.
        '''
        self.assertEqual('bla', parser._strip_all('bla'))
        self.assertEqual('bla', parser._strip_all('"bla"'))
        self.assertEqual('bla', parser._strip_all(' bla '))
        self.assertEqual('bla', parser._strip_all('"bla'))
        self.assertEqual('bla', parser._strip_all('bla" '))
        self.assertEqual('  bla', parser._strip_all('"  bla" '))
        self.assertEqual('some text', parser._strip_all('"some text" '))

    def test_get_attributes_for_sanity(self):
        '''
        Verifies the parsing of attributes.
        '''
        self.assertEquals(parser.get_attributes('foo=bar'), ('foo', 'bar'))
        self.assertEquals(parser.get_attributes('foo=bar '), ('foo', 'bar'))
        self.assertEquals(parser.get_attributes('foo= "some stuff"'),
                          ('foo', 'some stuff'))
        self.assertEquals(parser.get_attributes('foo = "bar"'),
                          ('foo', 'bar'))
