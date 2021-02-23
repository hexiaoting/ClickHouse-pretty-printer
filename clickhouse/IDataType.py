from typing import Tuple
import gdb

class IDataTypePrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "(*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+")).getName()"
#        print(eval_string)
        type_name=gdb.parse_and_eval(eval_string)
        #eval_string = "info vtbl (*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+"))"
        #type_name=gdb.execute(eval_string,  to_string=True).split('\n')[1].split("::")[1]

        return "IDataType = {}".format(type_name)

    def display_hint(self) -> str:
        return "IDataType"
