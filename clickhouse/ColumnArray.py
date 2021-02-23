from typing import Tuple
import gdb

class ColumnArrayPrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "(*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+")).size()"
        size=gdb.parse_and_eval(eval_string);
        return "ColumnArray size={}".format(size)

    def display_hint(self) -> str:
        return "array"
