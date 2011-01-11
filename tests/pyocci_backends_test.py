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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
Created on Nov 18, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.backends import Backend
import unittest

class BackendTest(unittest.TestCase):

    backend = Backend()

    def test_if_errors_are_thrown(self):
        self.assertRaises(NotImplementedError, self.backend.create, None)
        self.assertRaises(NotImplementedError, self.backend.retrieve, None)
        self.assertRaises(NotImplementedError, self.backend.update, None, None)
        self.assertRaises(NotImplementedError, self.backend.delete, None)
        self.assertRaises(NotImplementedError, self.backend.action, None, None)

if __name__ == "__main__":
    unittest.main()
