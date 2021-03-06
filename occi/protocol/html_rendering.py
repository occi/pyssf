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
Non OCCI specific rendering for HTML.

Created on Jul 15, 2011

@author: tmetsch
'''

# disabling 'Method is abstract' pylint check (HTML only support GET!)
# pylint: disable=W0223

from occi.core_model import Resource, Link
from occi.protocol.occi_rendering import Rendering


class HTMLRendering(Rendering):
    '''
    A simple HTML website rendering for monitoring the service...
    '''

    mime_type = 'text/html'

    css = "body { \
            font-family: sans-serif; \
            font-size: 0.9em; \
            margin: 0; \
            padding: 0; \
           } \
           #header { \
            background: #444; \
            border-top: 5px solid #73c167; \
           }  \
           #header ul { \
            list-style-type: none; \
            list-style-image: none; \
            margin: 0; \
            padding: 0; \
            height: 2em; \
           } \
           #header li { \
            margin: 0.3em 0.5em 0.3em 0.5em; \
            font-weight: bold; \
            display: inline-block; \
           } \
           #header li a { \
            padding: 0.3em; \
            text-decoration: none; \
            color: #fff; \
           } \
           #header li a:hover { \
            background: #73c167;\
            border-bottom: 2px solid #73c167; \
           } \
           #breadcrumb { \
            background: #efefea; \
            padding: 1em; \
            border-bottom: 1px solid #444; \
           } \
           td { \
            padding:  0.2em; \
            background: #eee; \
            color: #444; \
           } \
           table { \
            margin: 0 0 1em 1em; \
           } \
           table ul { \
            margin: 0.3em; \
           } \
           th { \
            background: #73c167; \
            padding:  0.2em; \
            color: #fff; \
           } \
           h2 { \
            margin: 1em; \
            font-size: 1.2em; \
            color: #444; \
           } \
           a { \
            color: #73c167; \
           } \
           #entity { \
            margin: 1em; \
           }"

    def __init__(self, registry, css=None):
        '''
        Constructor for HTML rendering. Can be used to use other CSS.

        registry -- Registry used in this service.
        css -- If provided this CSS is used.
        '''
        Rendering.__init__(self, registry)
        if css is not None:
            self.css = css

    def from_entity(self, entity):
        tmp = '<html>\n\t<head>\n'
        tmp += '\t\t<title>Resource: ' + entity.identifier + '</title>\n'
        tmp += '\t\t<style type="text/css"><!-- ' + self.css + ' --></style>\n'
        tmp += '\t</head>\n\t<body>\n'

        # header
        tmp += '\t\t<div id="header"><ul><li><a href="/">Home</a></li>'
        tmp += '<li><a href="/-/">Query Interface</a></li></ul></div>\n'

        # breadcrumb
        tmp += '\t\t<div id="breadcrumb"><a href="/">&raquo;</a> /'
        path = '/'
        for item in entity.identifier.split('/')[1:-1]:
            path += item + '/'
            tmp += ' <a href="' + path + '">' + item + "</a> / "
        tmp += entity.identifier.split('/')[-1]
        tmp += '</div>\n'

        # body
        tmp += '\t\t<div id="entity">\n'
        tmp += '\t\t\t<h2>Kind</h2><ul><li>'
        tmp += str(entity.kind) + '</li></ul>\n'
        if len(entity.mixins) > 0:
            tmp += '\t\t\t<h2>Mixins</h2><ul>'
            for item in entity.mixins:
                tmp += '<li>' + str(item) + '</li>'
            tmp += '</ul>\n'

        entity.attributes['occi.core.id'] = entity.identifier
        if isinstance(entity, Resource):
            if len(entity.links) > 0:
                tmp += '\t\t\t<h2>Links</h2><table>'
                tmp += '<tr><th>Kind</th><th>Link</th><th>Target</th></tr>'
                for item in entity.links:
                    tmp += '<tr><td>' + item.kind.term + '</td>'
                    tmp += '<td><a href="' + item.identifier + '">'
                    tmp += item.identifier + '</a></td>'
                    tmp += '<td><a href="' + item.target.identifier + '">'
                    tmp += item.target.identifier + '</a></td>'
                    tmp += '</tr>'
                tmp += '</table>\n'

        elif isinstance(entity, Link):
            tmp += '\t\t\t<h2>Source &amp; Target</h2><ul>'
            tmp += '<li><strong>Source: </strong>'
            tmp += '<a href="' + entity.source.identifier + '">'
            tmp += entity.source.identifier + '</a></li>'
            tmp += '<li><strong>Target: </strong>'
            tmp += '<a href="' + entity.target.identifier + '">'
            tmp += entity.target.identifier + '</a></li></ul>\n'

        if len(entity.attributes.keys()) > 0:
            tmp += '\t\t\t<h2>Attributes</h2><table>'
            for item in entity.attributes.keys():
                tmp += '<tr><th>' + item + '</th><td>'
                tmp += str(entity.attributes[item]) + '</td></tr>'
            tmp += '</table>\n'

        if len(entity.actions) > 0:
            tmp += '\t\t\t<h2>Actions</h2><ul>'
            for action in entity.actions:
                tmp += '<li>' + str(action.term) + '</li>'
            tmp += '<ul>\n'

        tmp += '\t\t</div>\n\t</body>\n</html>'
        return {}, tmp

    def from_entities(self, entities, key):
        tmp = '<html>\n\t<head>\n'
        tmp += '\t\t<title>Resource listing: ' + key + '</title>\n'
        tmp += '\t\t<style type="text/css"><!-- ' + self.css + ' --></style>\n'
        tmp += '\t</head>\n'
        tmp += '\t<body>\n'

        # header
        tmp += '\t\t<div id="header"><ul><li><a href="/">Home</a></li>'
        tmp += '<li><a href="/-/">Query Interface</a></li></ul></div>\n'

        # breadcrumb
        tmp += '\t\t<div id="breadcrumb"><a href="/">&raquo;</a> /'
        path = '/'
        for item in key.split('/')[1:-1]:
            path += item + '/'
            tmp += ' <a href="' + path + '">' + item + "</a> /"
        tmp += '</div>\n'

        # body
        tmp += '\t\t<div id="entity"><ul>\n'
        if len(entities) == 0:
            tmp += '\t\t\t<li>No resources found</li>\n'
        for item in entities:
            tmp += '\t\t\t<li><a href="' + item.identifier + '">'
            tmp += item.identifier + '</a></li>\n'
        tmp += '\t\t</ul></div>\n'
        tmp += '\t</body>\n</html>'
        return {}, tmp

    def from_categories(self, categories):
        tmp = '<html>\n\t<head>\n'
        tmp += '\t\t<title>Query Interface</title>\n'
        tmp += '\t\t<style type="text/css"><!-- ' + self.css + ' --></style>\n'
        tmp += '\t</head>\n'
        tmp += '\t<body>\n'

        # header
        tmp += '\t\t<div id="header"><ul><li><a href="/">Home</a></li>'
        tmp += '<li><a href="/-/">Query Interface</a></li></ul></div>\n'

        # breadcrumb
        tmp += '\t\t<div id="breadcrumb"><a href="/">&raquo;</a> /</div>\n'

        # body
        for cat in categories:
            tmp += '\t\t<h2>' + repr(cat).upper() + ': ' + cat.term + '</h2>\n'
            tmp += '\t\t<table>\n'
            tmp += '\t\t\t<tr><th>Scheme</th><td>' + cat.scheme
            tmp += '</td></tr>\n'
            if hasattr(cat, 'title') and cat.title is not '':
                tmp += '\t\t\t<tr><th>Title</th><td>' + cat.title
                tmp += '</td></tr>\n'
            if hasattr(cat, 'related') and len(cat.related) > 0:
                rel_list = '<ul>'
                for item in cat.related:
                    rel_list += '<li>' + str(item) + '</li>'
                rel_list += '</ul>'
                tmp += '\t\t\t<tr><th>Related</th><td>' + rel_list
                tmp += '</td></tr>\n'
            if hasattr(cat, 'location') and cat.location is not None:
                tmp += '\t\t\t<tr><th>Location</th><td><a href="'
                tmp += cat.location + '">' + cat.location + '</a></td></tr>\n'
            if hasattr(cat, 'actions') and len(cat.actions) > 0:
                acts = '<ul>'
                for item in cat.actions:
                    acts += '<li>' + str(item) + '</li>'
                acts += '</ul>'
                tmp += '\t\t\t<tr><th>Actions</th><td>' + acts + '</td></tr>\n'
            if hasattr(cat, 'attributes') and len(cat.attributes) > 0:
                attrs = '<ul>'
                for item in cat.attributes:
                    if cat.attributes[item] == 'required':
                        attrs += '<li>' + item
                        attrs += ' (<strong>required</strong>)</li>'
                    elif cat.attributes[item] == 'immutable':
                        attrs += '<li>' + item
                        attrs += ' (<strong>immutable</strong>)</li>'
                    else:
                        attrs += '<li>' + item + '</li>'
                attrs += '</ul>'
                tmp += '\t\t\t<tr><th>Attributes</th><td>' + attrs
                tmp += '</td></tr>\n'
            tmp += '\t\t</table>\n'

        tmp += '\t</body>\n</html>'
        return {}, tmp
