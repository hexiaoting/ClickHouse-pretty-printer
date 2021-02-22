from typing import Tuple
import gdb

class IASTPrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "info vtbl (*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+"))"
        #example: "info vtbl (*(DB::IAST *)(0x7fff472e9b18))"
        type_name=gdb.execute(eval_string,  to_string=True).split('\n')[1].split("::")[1]

        #eval_string = "DB::queryToString(*("+str(self.val.type).strip('&')+"*)("+str(self.val.address)+"))"
        eval_string = "DB::serializeAST(*(DB::"+type_name+" *)("+str(self.val.address)+"), true)"
        sql_string=gdb.parse_and_eval(eval_string);

        return "type={}, sql={}      ".format(type_name, sql_string)

    def display_hint(self) -> str:
        return "IAST"
