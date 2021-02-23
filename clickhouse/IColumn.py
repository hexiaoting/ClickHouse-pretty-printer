from typing import Tuple
import gdb

class IColumnPrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "(*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+")).getName()"
        #print(eval_string)
        type_name=gdb.parse_and_eval(eval_string)
        #print(type_name)
        eval_size_string= "(*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+")).size()"
        size=gdb.parse_and_eval(eval_size_string)

        return "type={}, size={}.".format(type_name,size)

    def display_hint(self) -> str:
        return "IColumn"
