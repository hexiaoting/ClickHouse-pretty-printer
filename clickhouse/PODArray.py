from typing import Tuple
import gdb

class PODArrayPrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    class CHIterator:
        def __init__(self, start: gdb.Value, finish: gdb.Value) -> None:
            self.item: gdb.Value = start
            self.finish: gdb.Value = finish
            self.count: int = 0

        def __iter__(self):
            return self

        def __next__(self):
            count: int = self.count
            self.count += 1

            if self.item == self.finish:
                raise StopIteration

            elt = self.item.dereference()
            self.item += 1

            return ('[%d]'.format(count), elt)

    def get_bounds(self) -> Tuple[int, int, int]:
        return self.val['c_start'], self.val['c_end'], self.val['c_end_of_storage']

    def to_string(self) -> str:
        start, finish, end = self.get_bounds()

        return ('{} of length {}, capacity {}'.format(
            self.val.type,
            int(finish - start),
            int(end - start)))

    def children(self) -> CHIterator:
        return self.CHIterator(
            self.val['c_start'],
            self.val['c_end'])

    def display_hint(self) -> str:
        return "array"
