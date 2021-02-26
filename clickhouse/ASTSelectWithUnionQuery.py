from typing import Tuple
import gdb

class ASTSelectWithUnionQueryPrinter:
    def __init__(self,  val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "info vtbl (*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+"))"
        #example: "info vtbl (*(DB::IAST *)(0x7fff472e9b18))"
        type_name=gdb.execute(eval_string,   to_string=True).split('\n')[1].split("::")[1]

        #eval_string = "DB::queryToString(*("+str(self.val.type).strip('&')+"*)("+str(self.val.address)+"))"
        eval_string = "DB::serializeAST(*(DB::"+type_name+" *)("+str(self.val.address)+"),  true)"
        sql_string=gdb.parse_and_eval(eval_string)

        union_mode=self.val["union_mode"]
        is_normalized=self.val["is_normalized"]
        out_file=self.val["out_file"]
        format_ast=self.val["format"]
        settings_ast=self.val["settings_ast"]
        list_of_modes=self.val["list_of_modes"]
        list_of_selects=self.val["list_of_selects"]

        #return "type={},  sql={}".format(type_name,  sql_string)
        return "type={}, sql={}, union_mode={}, is_normalized={}, out_file={}, format={}, settings_ast={}, list_of_modes={}, list_of_select={}".format(type_name,  sql_string,  union_mode, is_normalized, out_file, format_ast, settings_ast, list_of_modes, list_of_selects)

    def display_hint(self) -> str:
        return "ASTSelectWithUnionQuery"
