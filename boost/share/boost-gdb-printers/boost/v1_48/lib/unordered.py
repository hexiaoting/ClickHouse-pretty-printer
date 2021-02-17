# -*- tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-
# Helper classes for working with Boost.Unordered.
#
# This file is part of boost-gdb-printers.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gdb
import six

class Unordered(object):
    '''Common representation of Boost.Unordered types'''

    def __init__(self, value, extractor):
        self.value = value
        self.extractor = extractor
        self.node_type = None
        self.value_type = None
        self.extra_node = False
        self._init()

    def __len__(self):
        table = self.value['table_']
        if table['buckets_']:
            return int(table['size_'])
        else:
            return 0

    def __iter__(self):
        table = self.value['table_']
        buckets = table['buckets_']
        if buckets:
            start_bucket = buckets + table['bucket_count_']
            start_node = start_bucket.dereference()['next_']
            if self.extra_node:
                start_node = start_node.dereference()['next_']
            return self._iterator(start_node, self.node_type, self.value_type, self.extractor)
        else:
            return iter([])

    def empty(self):
        return not self.value['table_']['buckets_']

    def _init(self):
        table = self.value['table_'].type.fields()[0]
        assert table.is_base_class
        buckets = table.type.fields()[0]
        assert buckets.is_base_class

        alloc_type = buckets.type.template_argument(0)
        self.value_type = alloc_type.template_argument(0)

        bucket_type = buckets.type.template_argument(1).strip_typedefs()
        self.extra_node = (str(bucket_type) == 'boost::unordered::detail::bucket')

        self.node_type = buckets.type.template_argument(2)

    class _iterator(six.Iterator):
        '''Iterator for Boost.Unordered types'''

        def __init__(self, start_node, node_type, value_type, extractor):
            assert start_node
            self.node = None
            self.next_node = start_node
            self.node_type = node_type
            self.value_type = value_type
            self.extractor = extractor

        def __iter__(self):
            return self

        def __next__(self):
            # sorry, no next node available
            if not self.next_node or self.next_node == self.node:
                raise StopIteration()

            # fetch next node
            self.node = self.next_node
            self.next_node = self.node.dereference()['next_']

            mapped = self._value()
            return (self.extractor.key(mapped), self.extractor.value(mapped))

        def _value(self):
            assert self.node
            node = self.node.dereference().cast(self.node_type)
            return node['data_'].cast(self.value_type)

class Map(Unordered):

    def __init__(self, value):
        super(Map, self).__init__(value, self._extractor())

    class _extractor(object):

        def key(self, node):
            return node['first']

        def value(self, node):
            return node['second']

class Set(Unordered):

    def __init__(self, value):
        super(Set, self).__init__(value, self._extractor())

    class _extractor(object):

        def key(self, node):
            return None

        def value(self, node):
            return node

# vim:set filetype=python shiftwidth=4 softtabstop=4 expandtab:
