import ast
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from CodeGen.xgenBase import *
from CodeGen.xgenAST_Classes import *
from CodeGen.xgen_v_function import *

def get_subclasses(astList,BaseName):
    for astObj in astList:
        if  type(astObj).__name__ == 'ClassDef' and 'v_class' in [x.id  for x in astObj.bases]:
            yield astObj


class xgenAST:

    def __init__(self,sourceFileName):
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.parent = None
        self.sourceFileName =sourceFileName
        self._unfold_argList ={
            "Call" : Unfold_call,
            "Num" : unfold_num 
        }

        self.functionNameVetoList = list()
        self.functionNameVetoList.append("__init__")

        self._unfold_symbol_fun_arg={
    "port_in" : port_in_to_vhdl,
    "port_out" : port_out_to_vhdl,
    "v_slv"  : v_slv_to_vhdl,
    "v_sl"  : v_sl_to_vhdl
    }

        self._Unfold_body={
            "FunctionDef"   : body_unfold_functionDef,
            "Return"        : body_unfold_return,
            "Compare"       : body_unfold_Compare,
            "Attribute"     : body_unfold_Attribute,
            "Num"           : body_unfold_Num,
            "Assign"        : body_unfold_assign,
            "Name"          : body_unfold_Name,
            "Call"          : body_unfold_call,
            "Expr"          : body_expr,
            "BinOp"         : body_BinOP,
            "LShift"        : body_LShift,
            "Str"           : body_unfold_str,
            'NameConstant'  : body_Named_constant,
            "If"            : body_if,
            "list"          : body_list,
            "BoolOp"        : body_BoolOp,
            "UnaryOp"       : body_UnaryOP,
            "Add"           : body_add,
            'Subscript'     : body_subscript,
            "Index"          : body_index

        }
        with open(sourceFileName, "r") as source:
            self.tree = ast.parse(source.read())

        self.ast_v_classes = list(get_subclasses(self.tree.body,'v_class'))


    def get_variable(self,name, Node):
            
        for x in self.LocalVar:
            if name in x.vhdl_name:
                return x


        for x in self.FuncArgs:
            if name in x["name"]:
                return x["symbol"]

        raise Exception(Node_line_col_2_str(self, Node)+"Unable to find variable: " + name)

    def getClassByName(self,ClassName):
        for x in self.ast_v_classes:
            if x.name == ClassName:
                return x

        raise Exception("unable to find v_class '" + ClassName +"' in source '"+ self.sourceFileName+"'")


    def get_local_var_def(self):
        ret =""
        for x in self.LocalVar:
            ret += x._vhdl__DefineSymbol()
        
        return ret
    def extractFunctionsForClass(self,ClassInstance,parent ):
        
        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            if  f.name in self.functionNameVetoList:
                continue
            self.parent = parent
            self.FuncArgs = list()
            self.LocalVar = list()
            ArglistProcedure = ""
            Arglist = list(self.get_func_args_list(f))
            for x in Arglist:
                ArglistProcedure =  "; "  + x["symbol"].to_arglist(x['name'],ClassName) + ArglistProcedure



            ArglistProcedure = "self : inout "+ClassInstance.name + ArglistProcedure
            ClassInstance.set_vhdl_name ( "self")
            ClassInstance.Inout  = InOut_t.InOut_tt
            Arglist.append(
                {
                    "name":"self",
                    "symbol": ClassInstance,
                    "ScopeType": InOut_t.InOut_tt

                }
            )
            self.FuncArgs = Arglist
            body = self.Unfold_body(f)
            bodystr= str(body)
            if "return" in bodystr:
                ArglistProcedure = ArglistProcedure.replace(" in "," ").replace(" out "," ").replace(" inout "," ")
                ret = v_function(name=f.name, body=bodystr,VariableList=self.get_local_var_def(), returnType=body.get_type(),argumentList=ArglistProcedure)
            else:
                ret = v_procedure(name=f.name,body=bodystr,VariableList=self.get_local_var_def(), argumentList=ArglistProcedure)
                
            yield ret 


    def Unfold_body(self,FuncDef):
        ftype = type(FuncDef).__name__
        return self._Unfold_body[ftype](self,FuncDef)

    def unfold_argList(self,x):
        x_type = type(x).__name__
        return self._unfold_argList[x_type](self, x)

    def getInstantByName(self,SymbolName):
        if issubclass(type(SymbolName),vhdl_base):
            return SymbolName

        for x in self.FuncArgs:
            if x["name"] == SymbolName:
                return x["symbol"]

        for x in self.LocalVar:
            if x.vhdl_name == SymbolName:
                return x

        if self.parent:
            ret = self.parent.getInstantByName(SymbolName)
            if ret:
                return ret 
                

        raise Exception("Unable to find symbol", SymbolName, "\nAvalible Symbols\n",self.Arglist)





    def get_func_args(self, funcDef):
        for i in range(len(funcDef.args.args),1,-1):
            yield (funcDef.args.args[i-1].arg,funcDef.args.defaults[i-2])

    def get_func_args_list(self, funcDef):
        
    
        for args in self.get_func_args(funcDef): 
            inArg = self.unfold_argList(args[1])
            inArg = to_v_object(inArg)
            inArg.set_vhdl_name(args[0])
            yield {
                    "name": args[0],
                    "symbol": inArg
                }

