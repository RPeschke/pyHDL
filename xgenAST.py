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
        if  type(astObj).__name__ == 'ClassDef' and BaseName in [x.id  for x in astObj.bases]:
            yield astObj

dataType_ = list()
def dataType(astParser=None, args=None):
    Name = None
    if args:
        Name = args[0]

    if dataType_:
        if Name == None:
            return dataType_[-1]["symbol"]
        
        else:
            for x in dataType_:
                if x["name"] == Name:
                    return x["symbol"]
            raise Exception("unknown data type")

    return v_slv()

def AddDataType(dType,Name=""):
    dataType_.append(
        {
            "name"   : Name,
            "symbol" : copy.deepcopy( dType)
        }
    )
class xgenAST:

    def __init__(self,sourceFileName):
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.varScope = list()

        self.ContextName = list()
        self.ContextName.append("global")
        self.Context = None
        self.parent = None
        self.sourceFileName =sourceFileName
        self._unfold_argList ={
            "Call" : Unfold_call,
            "Num" : unfold_num,
            "Str" : unfold_Str
           
        }

        self.functionNameVetoList = [
        "__init__",
        "create",
        "__lshift__",
        "__bool__",
        '_vhdl__to_bool',
        '_vhdl__getValue',
        "_vhdl__reasign",
        '_connect',
        "_sim_get_value"
        ]

        self.local_function ={}
        self._unfold_symbol_fun_arg={
    "port_in" : port_in_to_vhdl,
    "port_out" : port_out_to_vhdl,
    "v_slv"  : v_slv_to_vhdl,
    "v_sl"  : v_sl_to_vhdl,
    "v_int" : v_int_to_vhdl,
    "v_bool" : v_bool_to_vhdl,
    "dataType":dataType,
     "rising_edge" : handle_rising_edge,
     "print"       : handle_print
  #   "v_create"    : handle_v_create
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
            'RShift'        : body_RShift,
            "BitOr"         : body_bitOr,
            "Str"           : body_unfold_str,
            'NameConstant'  : body_Named_constant,
            "If"            : body_if,
            "list"          : body_list,
            "BoolOp"        : body_BoolOp,
            "UnaryOp"       : body_UnaryOP,
            "Add"           : body_add,
            'Subscript'     : body_subscript,
            "Index"         : body_index,
            'Yield'         : body_unfold_yield
        }
        with open(sourceFileName, "r") as source:
            self.tree = ast.parse(source.read())

        self.ast_v_classes = list(get_subclasses(self.tree.body,'v_class'))
        self.ast_v_Entities = list(get_subclasses(self.tree.body,'v_entity'))
        self.ast_v_Entities.extend( list(get_subclasses(self.tree.body,'v_clk_entity')))
    
    def AddStatementBefore(self,Statement):
        if not self.Context == None:
            self.Context.append(Statement)

    def push_scope(self,NewContextName=None):
        
        if not NewContextName:
            NewContextName = self.ContextName[-1]
        self.ContextName.append(NewContextName)

        self.varScope.append(self.LocalVar)
        self.LocalVar = list()

    def get_scope_name(self):
        return self.ContextName[-1]


    def pop_scope(self):
        self.LocalVar =  self.varScope[-1]
        del self.varScope[-1]
        del self.ContextName[-1]
        


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
        for x in self.ast_v_Entities:
            if x.name == ClassName:
                return x

        raise Exception("unable to find v_class '" + ClassName +"' in source '"+ self.sourceFileName+"'")


    def get_local_var_def(self):
        ret =""
        for x in self.LocalVar:
            ret += x._vhdl__DefineSymbol()
        
        return ret

    def extractArchetectureForEntity(self, ClassInstance, parent):
        setDefaultVarSig(varSig.signal_t)

        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            self.local_function ={}
            if  f.name in self.functionNameVetoList:
                continue
            print(f.name)
            self.parent = parent
            self.FuncArgs = list()
            self.LocalVar = list()
            self.FuncArgs.append(
                {
                    "name":"self",
                    "symbol": ClassInstance,
                    "ScopeType": InOut_t.InOut_tt

                }
            )
            #p=ClassInstance._process1()
            
            #self.local_function = p.__globals__
            self.local_function = ClassInstance.__init__.__globals__
            body = self.Unfold_body(f)  ## get local vars 

            header =""
            for x in self.LocalVar:
                if x.type == "undef":
                    continue
                if  hasattr(x, 'varSigConst') and x.varSigConst == varSig.variable_t:
                    continue
                header += x._vhdl__DefineSymbol("signal")
            
            proc = v_Arch(body=str(body),Header=header)
            ClassInstance.__processList__.append(proc)

    def extractFunctionsForEntity(self, ClassInstance, parent):
        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            self.local_function ={}
            if  f.name in self.functionNameVetoList:
                continue
            print(f.name)
            self.parent = parent
            self.FuncArgs = list()
            self.LocalVar = list()
            self.FuncArgs.append(
                {
                    "name":"self",
                    "symbol": ClassInstance,
                    "ScopeType": InOut_t.InOut_tt

                }
            )
            #p=ClassInstance._process1()
            
            #self.local_function = p.__globals__
            self.local_function = ClassInstance.__init__.__globals__
            body = self.Unfold_body(f)  ## get local vars 

            header =""
            for x in self.LocalVar:
                if x.type == "undef":
                    continue
                header += x._vhdl__DefineSymbol("variable")

            pull =""
            for x in self.LocalVar:
                if x.type == "undef":
                    continue
                pull += x._vhdl__Pull()

            push =""
            for x in self.LocalVar:
                if x.type == "undef":
                    continue
                push += x._vhdl__push()
            
            for x in f.body:
                if type(x).__name__ == "FunctionDef":
                    b = self.Unfold_body(x)
                    body = str(b)  ## unfold function of intressed  
                    break
            
            body =pull +"\n" + body +"\n" + push
            
            proc = v_process(body=body, SensitivityList=b.dec[0].get_sensitivity_list(),prefix=b.dec[0].get_prefix(), VariableList=header)
            ClassInstance.__processList__.append(proc)
            


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

        for x in self.varScope:
            index = -1
            for y in x:
                index = index + 1
                if y.vhdl_name == SymbolName:
                    if y.varSigConst == varSig.variable_t:
                        self.LocalVar.append(y)
                        del x[index]
                        return y
                    
                    return y

        if self.parent:
            ret = self.parent.getInstantByName(SymbolName)
            if ret:
                return ret 
                
        try: 
            return self.local_function[SymbolName]
        except:
            pass
        
        
        raise Exception("Unable to find symbol", SymbolName, "\nAvalible Symbols\n",self.FuncArgs)





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

