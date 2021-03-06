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
Actual mime-type renderings.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi.core_model import Resource, Link
import occi.protocol.occi_parser as parser
import shlex


class HTTPData(object):
    '''
    Simple class which functions as an adapter between the OCCI model and the
    HTTP rendering. Holds all information in the way an entity is rendered.
    '''

    # disabling 'Too few public methods' pylint check (just a data model)
    # pylint: disable=R0903

    def __init__(self):
        self.categories = []
        self.links = []
        self.attributes = []
        self.locations = []


class Rendering(object):
    '''
    All renderings should derive from this class.
    '''

    def __init__(self, registry):
        '''
        Constructor.

        registry -- The registry used for this process.
        '''
        self.registry = registry

    def to_entity(self, headers, body, def_kind):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an entity representation. Must return Resource or Link
        instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        def_kind -- If provided this kind is taken (Needed for update).
        '''
        raise NotImplementedError()

    def from_entity(self, entity):
        '''
        Given an entity it will return a HTTP body an header.

        If it's a link make sure source, target attributes are set. If it's a
        Resource make sure Links are presented properly.

        entity -- The entity which is to rendered.
        '''
        raise NotImplementedError()

    def to_entities(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a set of entity representations. Must return a set of
        Resource or Link instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def from_entities(self, entities, key):
        '''
        Given an set of entities it will return a HTTP body an header.

        entities -- The entities which will be rendered.
        key -- Needed for uri-list (see RFC) and html rendering.
        '''
        raise NotImplementedError()

    def from_categories(self, categories):
        '''
        Given an set of categories it will return a HTTP body an header.

        categories -- The list of categories which is to be rendered.
        '''
        raise NotImplementedError()

    def to_action(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an Action.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def to_mixins(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a Mixins. Must return a list with Mixin instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def get_filters(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a list of categories and attributes.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

#==============================================================================
# text/occi rendering
#==============================================================================


def _extract_data_from_headers(headers):
    '''
    Simple method to split out the information from the HTTP headers.

    headers -- The HTTP headers.
    '''
    # split out the information
    data = HTTPData()
    if 'Category' in headers.keys():
        data.categories = headers['Category'].split(',')
    if 'X-OCCI-Attribute' in headers.keys():
        split = shlex.shlex(headers['X-OCCI-Attribute'], posix=True)
        split.whitespace += ','
        split.whitespace_split = True
        data.attributes = list(split)
    if 'X-OCCI-Location' in headers.keys():
        data.locations = headers['X-OCCI-Location'].split(',')
    if 'Link' in headers.keys():
        data.links = headers['Link'].split(',')
    return data


def _set_data_to_headers(data):
    '''
    Simple method to set all information in the HTTP header.

    data -- The data to set.
    '''
    headers = {}
    body = 'OK'

    if len(data.categories) > 0:
        headers['Category'] = ', '.join(data.categories)
    if len(data.links) > 0:
        headers['Link'] = ', '.join(data.links)
    if len(data.locations) > 0:
        headers['X-OCCI-Location'] = ', '.join(data.locations)
    if len(data.attributes) > 0:
        headers['X-OCCI-Attribute'] = ', '.join(data.attributes)

    return headers, body


def _to_entity(data, def_kind, registry):
    '''
    Extract an entity from the HTTP data object.

    kind -- The kind definition.
    registry -- The registry.
    '''

    # disable 'Too many local vars' pylint check (It's a bit ugly but will do)
    # disable 'Too many branches' pylint check (Needs to be improved)
    # pylint: disable=R0914,R0912

    kind = None
    mixins = []

    # first kind & mixins
    kind_found = False
    for category_string in data.categories:
        category = parser.get_category(category_string.strip(),
                                       registry.get_categories())
        if repr(category) == 'kind' and not kind_found:
            kind = category
            kind_found = True
        else:
            mixins.append(category)

    # the attributes
    attributes = {}
    for attr_string in data.attributes:
        key, value = parser.get_attributes(attr_string)
        attributes[key] = value

    # now create the entity
    if kind_found is False and def_kind is None:
        raise AttributeError('Could not find a valid kind.')
    elif def_kind is not None:
        kind = def_kind

    if Resource.kind in kind.related:
        # links
        entity = Resource(None, kind, mixins, [])
        for link_string in data.links:
            entity.links.append(parser.get_link(link_string.strip(),
                                                entity,
                                                registry))
    elif Link.kind in kind.related:
        try:
            source_attr = attributes['occi.core.source']
            target_attr = attributes['occi.core.target']

            if source_attr.find(registry.get_hostname()) == 0:
                source_attr = source_attr.replace(registry.get_hostname(), '')
            if target_attr.find(registry.get_hostname()) == 0:
                target_attr = target_attr.replace(registry.get_hostname(), '')

            source = registry.get_resource(source_attr)
            target = registry.get_resource(target_attr)
        except KeyError:
            raise AttributeError('Both occi.core.[source, target]'
                                 + ' attributes need to be resources.')
        entity = Link(None, kind, mixins, source, target)
    else:
        raise AttributeError('This kind seems not to be related to either'
                             + ' resource or link.')

    entity.attributes = attributes
    return entity


def _from_entity(entity):
    '''
    Create a HTTP data object from an entity.

    entity -- The entity to render.
    '''
    data = HTTPData()

    # categories
    cat_str_list = []
    cat_str_list.append(parser.get_category_str(entity.kind))

    for category in entity.mixins:
        cat_str_list.append(parser.get_category_str(category))

    data.categories = cat_str_list

    attributes = []
    entity.attributes['occi.core.id'] = entity.identifier

    link_str_list = []
    # actions
    for action in entity.actions:
        act = '<' + entity.identifier + '?action=' + action.term + '>'
        act = act + '; rel="' + str(action) + '"'
        link_str_list.append(act)

    # links
    if isinstance(entity, Resource):
        # links
        for link in entity.links:
            link_str_list.append(parser.get_link_str(link))

    elif isinstance(entity, Link):
        entity.attributes['occi.core.source'] = entity.source.identifier
        entity.attributes['occi.core.target'] = entity.target.identifier

    data.links = link_str_list

    # attributes
    for attr in entity.attributes:
        attributes.append(attr + '="'
                          + entity.attributes[attr] + '"')

    data.attributes = attributes

    return data


def _to_entities(data, registry):
    '''
    Extract a set of (in the service existing) entities from a request.

    data -- the HTTP data.
    registry -- The registry used for this call.
    '''
    result = []
    for item in data.locations:
        try:
            if item.find(registry.get_hostname()) == 0:
                item = item.replace(registry.get_hostname(), '')

            result.append(registry.get_resource(item.strip()))
        except KeyError:
            raise AttributeError('Could not find the resource with id: '
                                 + str(item))

    return result


def _from_entities(entity_list, registry):
    '''
    Return a list of entities using the X-OCCI-Location attribute.

    entity_list -- list of entities.
    registry -- The registry used for this call.registry
    '''
    data = HTTPData()
    for entity in entity_list:
        data.locations.append(registry.get_hostname() + entity.identifier)

    return data


def _from_categories(categories):
    '''
    Create a HTTP data object from a set of categories.

    categories -- list of categories.
    '''
    data = HTTPData()

    for cat in categories:
        data.categories.append(parser.get_category_str(cat))

    return data


def _to_action(data, registry):
    '''
    Create an action from an HTTP data object.

    data -- the HTTP data.
    registry -- The registry used for this call.
    '''
    action = parser.get_category(data.categories[0].strip(),
                                 registry.get_categories())

    return action


def _to_mixins(data, registry):
    '''
    Create a Mixin from an HTTP data object.

    data -- the HTTP data.
    registry -- The registry used for this call.
    '''
    result = []
    for cat_str in data.categories:
        result.append(parser.get_category(cat_str,
                                          registry.get_categories(),
                                          is_mixin=True))

    return result


def _get_filter(data, registry):
    '''
    Parse categories and attributes from the request.

    data -- the HTTP data.
    registry -- The registry used for this call.
    '''
    categories = []
    attributes = {}

    for cat in data.categories:
        categories.append(parser.get_category(cat, registry.get_categories()))

    for attr in data.attributes:
        key, value = parser.get_attributes(attr)
        attributes[key] = value

    return categories, attributes


class TextOcciRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'text/occi'

    # disabling 'Method could be...' pylint check (want them to be overwritten)
    # disabling 'Unused argument' pylint check (text/plain will use it :-))
    # pylint: disable=R0201,W0613

    def get_data(self, headers, body):
        '''
        Mainly here so TextPlainRendering can reuse.

        headers -- The headers of the request.
        body -- The body of the request.
        '''
        return _extract_data_from_headers(headers)

    def set_data(self, data):
        '''
        Mainly here so TextPlainRendering can reuse.

        data -- An HTTPData object.
        '''
        return _set_data_to_headers(data)

    def to_entity(self, headers, body, def_kind):
        data = self.get_data(headers, body)
        entity = _to_entity(data, def_kind, self.registry)
        return entity

    def from_entity(self, entity):
        data = _from_entity(entity)
        headers, body = self.set_data(data)
        return headers, body

    def to_entities(self, headers, body):
        data = self.get_data(headers, body)
        entities = _to_entities(data, self.registry)
        return entities

    def from_entities(self, entities, key):
        data = _from_entities(entities, self.registry)
        headers, body = self.set_data(data)
        return headers, body

    def from_categories(self, categories):
        data = _from_categories(categories)
        headers, body = self.set_data(data)
        return headers, body

    def to_action(self, headers, body):
        data = self.get_data(headers, body)
        action = _to_action(data, self.registry)
        return action

    def to_mixins(self, headers, body):
        data = self.get_data(headers, body)
        mixin = _to_mixins(data, self.registry)
        return mixin

    def get_filters(self, headers, body):
        data = self.get_data(headers, body)
        categories, attributes = _get_filter(data, self.registry)
        return categories, attributes


def _extract_data_from_body(body):
    '''
    Simple method to split out the information from the HTTP body.

    body -- The HTTP body.
    '''
    data = HTTPData()
    for entry in body.split('\n'):
        if entry.find('Category:') > -1:
            data.categories.extend(_extract_values(entry, 'Category:'))
        if entry.find('X-OCCI-Attribute:') > -1:
            data.attributes.extend(_extract_values(entry, 'X-OCCI-Attribute:'))
        if entry.find('Link:') > -1:
            data.links.extend(_extract_values(entry, 'Link:'))
        if entry.find('X-OCCI-Location:') > -1:
            data.locations.extend(_extract_values(entry, 'X-OCCI-Location:'))
    return data


def _extract_values(entry, key):
    '''
    In HTTP body OCCI renderings can either be in new lines or separated by ,.

    entry -- The text line to look into.
    key -- The key to look for and strip away.
    '''
    items = []
    tmp = entry[entry.find(key) + len(key) + 1:]
    if tmp.find(',') == -1:
        items.append(tmp)
    else:
        split = shlex.shlex(tmp, posix=True)
        split.whitespace += ','
        split.whitespace_split = True
        items.extend(list(split))
    return items


def _set_data_to_body(data):
    '''
    Simple method to set all information in the HTTP body.

    data -- The data to set.
    '''
    body = ''
    if len(data.categories) > 0:
        for cat in data.categories:
            body += '\nCategory: ' + cat

    if len(data.links) > 0:
        for link in data.links:
            body += '\nLink: ' + link

    if len(data.attributes) > 0:
        for attr in data.attributes:
            body += '\nX-OCCI-Attribute: ' + attr

    if len(data.locations) > 0:
        for loc in data.locations:
            body += '\nX-OCCI-Location: ' + loc

    return {}, body


class TextPlainRendering(TextOcciRendering):
    '''
    This is a rendering which will use the HTTP body to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'text/plain'

    def set_data(self, data):
        return _set_data_to_body(data)

    def get_data(self, headers, body):
        return _extract_data_from_body(body)


class TextUriListRendering(Rendering):
    '''
    This is a rendering which can handle URI lists.
    '''

    mime_type = 'text/uri-list'
    error = 'Unable to handle this request with the text/uri-list' \
                ' rendering.'

    def to_entity(self, headers, body, def_kind):
        raise AttributeError(self.error)

    def from_entity(self, entity):
        raise AttributeError(self.error)

    def to_entities(self, headers, body):
        raise AttributeError(self.error)

    def from_entities(self, entities, key):
        body = '# uri:' + str(key)
        for entity in entities:
            body += '\n' + self.registry.get_hostname() + entity.identifier
        return {}, body

    def from_categories(self, categories):
        raise AttributeError(self.error)

    def to_action(self, headers, body):
        raise AttributeError(self.error)

    def to_mixins(self, headers, body):
        raise AttributeError(self.error)

    def get_filters(self, headers, body):
        raise AttributeError(self.error)
