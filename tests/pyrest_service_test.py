# 
# Copyright (C) 2010 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
'''
Created on Jul 5, 2010

@author: tmetsch
'''
from pyrest import service
import unittest

class ResourceCreationTests(unittest.TestCase):

    # request("/hello",
    #        method = 'GET',
    #        data = None,
    #        host = '0.0.0.0:8080',
    #        headers = None,
    #        https = False)

    # --------
    # TEST FOR SUCCESS
    # --------

    heads = {'Category': 'compute;scheme="http://purl.org/occi/kind#";label="Compute Resource"'}

    def test_post_for_success(self):
        # simple post on entry point should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        #response = service.APPLICATION.request("/job/", method = "POST")
        #self.assertEquals(response.status, '200 OK')

    def test_get_for_success(self):
        # simple post and get on the returned location should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.status, '200 OK')

        # get on */ should return listing
        response = service.APPLICATION.request("/")
        self.assertEquals(response.status, '200 OK')
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_success(self):
        # Put on specified resource should return 200 OK (non-existent)
        response = service.APPLICATION.request("/123", method = "PUT", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        # put on existent should update
        response = service.APPLICATION.request("/123", method = "PUT", headers = self.heads, data = "hello")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_success(self):
        # Del on created resource should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc, method = "DELETE")
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_post_for_failure(self):
        # post to non-existent resource should return 404
        response = service.APPLICATION.request("/123", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '404 Not Found')

    def test_get_for_failure(self):
        # get on non existent should return 404
        response = service.APPLICATION.request("/123")
        self.assertEquals(response.status, '404 Not Found')

    def test_put_for_failure(self):
        # maybe test invalid data ?
        pass

    def test_delete_for_failure(self):
        # delete of non existent should return 404
        response = service.APPLICATION.request("/123", method = "DELETE")
        self.assertEquals(response.status, '404 Not Found')

    # --------
    # TEST FOR SANITY
    # --------

    def test_post_for_sanity(self):
        # first create (post) then get
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.data, 'some data')

        # post to existent url should create sub resource 
        # TODO

    def test_get_for_sanity(self):
        # first create (put) than test get on parent for listing
        service.APPLICATION.request("/job/123", method = "PUT", headers = self.heads, data = "hello")
        response = service.APPLICATION.request("/job/")
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_sanity(self):
        # put on existent should update
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.data, "some data")
        response = service.APPLICATION.request(loc, method = "PUT", headers = self.heads, data = "other data")
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request(loc)
        # TODO needs proper backend!
        #self.assertEquals(response.data, "other data")

        # put on non-existent should create
        response = service.APPLICATION.request("/abc", method = "PUT", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request("/abc")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_sanity(self):
        # create and delete an entry than try get
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        service.APPLICATION.request(loc, method = "DELETE")
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.status, "404 Not Found")

class CategoriesTests(unittest.TestCase):

    # Note: more tests are done in the parser tests
    heads = {'Category': 'job;scheme="http://purl.org/occi/kind#";label="Job Resource"'}

    def test_categories_for_failure(self):
        # if a post is done without category -> Fail
        response = service.APPLICATION.request("/", method = "POST")
        self.assertEquals('400 Bad Request', response.status)

    def test_categories_for_sanity(self):
        # if a post is done and later a get should return same category
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        cat = response.headers['Category'].split(';')
        self.assertEquals(cat[0], 'job')
        self.assertEquals(cat[1].split('=')[-1:].pop(), 'http://purl.org/occi/kind#')

class AttributeTests(unittest.TestCase):

    # Note: more tests are done in the parser tests

    heads = {'Category': 'job;scheme="http://purl.org/occi/kind#";label="Job Resource"', 'occi.drmaa.executable':'/bin/sleep'}

    def test_attributes_for_sanity(self):
        # pass along some attributes and see if they can be retrieved
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        #print response
        self.assertEquals(response.headers['occi.drmaa.executable'], '/bin/sleep')

class LinkTests(unittest.TestCase):

    # Note: more test are done in the parser tests
    heads = {'Category': 'job;scheme="http://purl.org/occi/kind#";label="Job Resource"', 'Link': '</123>;class="test";rel="http://example.com/next/job";title="Next job"'}

    def test_links_far_sanity(self):
        # pass along some attributes and see if they can be retrieved
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        self.assertEquals(response.headers['Link'].split(';')[0], '</123>')

class ActionsTests(unittest.TestCase):

    heads = {'Category': 'job;scheme="http://purl.org/occi/kind#";label="Job Resource"', 'occi.drmaa.executable':'/bin/sleep'}

    def test_trigger_action_for_success(self):
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url, method = "POST")
        self.assertEquals(response.status, '200 OK')

    def test_trigger_action_for_failure(self):
        # only post allowed!
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url, method = "PUT")
        self.assertEquals(response.status, '400 Bad Request')

        # trigger not existing action!
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url + 'all', method = "POST")
        self.assertEquals(response.status, '400 Bad Request')

        # trigger action on non existing resource
        response = service.APPLICATION.request('http://abc.com/all;kill', method = "POST")
        self.assertEquals(response.status, '404 Not Found')

    def test_trigger_action_for_sanity(self):
        # check if result is okay :-)
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        service.APPLICATION.request(kill_url, method = "POST")
        response = service.APPLICATION.request(url)
        self.assertEquals(response.headers['occi.drmaa.state'], 'killed')

class QueryTests(unittest.TestCase):
    pass

class SecurityTests(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
