from typing import Tuple
import gdb

class ASTSelectQueryPrinter:
    def __init__(self, val: gdb.Value) -> None:
        self.val: gdb.Value = val

    def to_string(self) -> str:
        eval_string = "info vtbl (*("+str(self.val.type).strip('&')+" *)("+str(self.val.address)+"))"
        #example: "info vtbl (*(DB::IAST *)(0x7fff472e9b18))"
        type_name=gdb.execute(eval_string,  to_string=True).split('\n')[1].split("::")[1]

        #eval_string = "DB::queryToString(*("+str(self.val.type).strip('&')+"*)("+str(self.val.address)+"))"
        eval_string = "DB::serializeAST(*(DB::"+type_name+" *)("+str(self.val.address)+"), true)"
        sql_string=gdb.parse_and_eval(eval_string)

        distinct=self.val["distinct"]
        group_by_with_totals=self.val["group_by_with_totals"]
        group_by_with_rollup=self.val["group_by_with_rollup"]
        group_by_with_cube=self.val["group_by_with_cube"]
        limit_with_ties=self.val["limit_with_ties"]
        positions=self.val["positions"]

        #return "type={}, sql={}".format(type_name, sql_string)
        return "type={}, sql={}, distinct={}, group_by_with_totals={}, group_by_with_rollup={}, group_by_with_cube={}, limit_with_tie={}, positions={}".format(type_name, sql_string,distinct,group_by_with_totals,group_by_with_rollup,group_by_with_cube,limit_with_ties,positions)

    def display_hint(self) -> str:
        return "ASTSelectQuery"
