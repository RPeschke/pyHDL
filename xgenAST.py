import ast
import os,sys,inspect
import time

import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
    from CodeGen.xgenAST_Classes import * 
    from CodeGen.xgen_v_function import *
else:
    from .xgenBase import *
    from .xgenAST_Classes import *
    from .xgen_v_function import *


import cProfile, pstats, io



def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


def checkIfFunctionexists(cl_instant, name, funcArg ):
    for x in cl_instant.hdl_conversion__.MemfunctionCalls:
        if x["name"] != name:
            continue
        
        if not isSameArgs(x["args"] ,funcArg):
            continue
        return True
    
    return False


def check_if_subclasses(BaseNames,baseclasses):
    for b in BaseNames:
        if b  in baseclasses:
            return True
    return False

def get_subclasses(astList,BaseNames):
    for astObj in astList:
        if  type(astObj).__name__ == 'ClassDef':
            baseclasses = [x.id  for x in astObj.bases]
            if  check_if_subclasses(BaseNames,baseclasses):
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


def GetNewArgList(FunctionName , FunctionArgs,TemplateDescription):

    
    if FunctionName != TemplateDescription["name"]:
        return None
    localArgs = copy.copy(FunctionArgs) #deepcopy
    for x,y in zip(localArgs,TemplateDescription["args"]):
        #print(x,y)
        if y == None:
            return None  
        if x["symbol"] == None or x["symbol"].type != y.type or x['symbol'].varSigConst != y.varSigConst:
            #y.Inout =  x["symbol"].Inout
            y.set_vhdl_name(x["name"],True)
            
            x["symbol"] = copy.deepcopy(y)
            x["symbol"]._writtenRead  = InOut_t.Internal_t
            x["symbol"].Inout  = InOut_t.Internal_t
            mem = x["symbol"].getMember()
            for m in mem:
                m["symbol"]._writtenRead  = InOut_t.Internal_t
                m["symbol"].Inout  = InOut_t.Internal_t
    return localArgs

    
class xgenAST:

    def __init__(self,sourceFileName):
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.varScope = list()
        self.Missing_template = False
        self.Archetecture_vars = list()
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
        "_sim_get_value",
        "get_master",
        "get_slave"

        ]

        self.local_function ={}
        self._unfold_symbol_fun_arg={
    "port_in" : port_in_to_vhdl,
    "port_out" : port_out_to_vhdl,
    "variable_port_in" :  variable_port_in_to_vhdl,
    "variable_port_out" : variable_port_out_to_vhdl,
    "v_slv"  : v_slv_to_vhdl,
    "v_sl"  : v_sl_to_vhdl,
    "v_int" : v_int_to_vhdl,
    "v_bool" : v_bool_to_vhdl,
    "dataType":dataType,
     "rising_edge" : handle_rising_edge,
     "print"       : handle_print,
     "v_switch"  : handle_v_switch,
     "v_case"    : handle_v_case,
     "len"       : body_handle_len
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
            "Sub"           : body_sub,
            'Subscript'     : body_subscript,
            "Index"         : body_index,
            'Yield'         : body_unfold_yield,
            "For"           : body_unfold_for
        }
        with open(sourceFileName, "r") as source:
            self.tree = ast.parse(source.read())

        self.ast_v_classes = list(get_subclasses(self.tree.body,['v_class','v_class_master',"v_class_slave"]))
        self.ast_v_Entities = list(get_subclasses(self.tree.body,['v_entity']))
        self.ast_v_Entities.extend( list(get_subclasses(self.tree.body,['v_clk_entity'])))
    
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
        
    def try_get_variable(self,name):
        for x in self.LocalVar:
            if name == x.vhdl_name:
                return x


        for x in self.FuncArgs:
            if name in x["name"]:
                return x["symbol"]
        return None

    def get_variable(self,name, Node):
        
        x  = self.try_get_variable(name)
        if x:
            return x

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
            ret += x.hdl_conversion__._vhdl__DefineSymbol(x)
        
        return ret

    def extractArchetectureForEntity(self, ClassInstance, parent):
        setDefaultVarSig(varSig.signal_t)

        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            self.Missing_template = False
            ClassInstance.hdl_conversion__.reset_TemplateMissing(ClassInstance)
            self.local_function ={}
            if  f.name in self.functionNameVetoList:
                continue
            # print(f.name)
            self.parent = parent
            self.FuncArgs = list()
            self.LocalVar = list()
            self.Archetecture_vars =[]
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
            self.Archetecture_vars = ClassInstance.__local_symbols__
            body = self.Unfold_body(f)  ## get local vars 

            if self.Missing_template == True:
                ClassInstance.hdl_conversion__.FlagFor_TemplateMissing(ClassInstance)
                ClassInstance.hdl_conversion__.MissingTemplate = True
            else:
                proc = v_Arch(body=body,Symbols=self.LocalVar, Arch_vars=self.Archetecture_vars,ports=ClassInstance.getMember())
                ClassInstance.__processList__.append(proc)

            return self

    def extractFunctionsForEntity(self, ClassInstance, parent):
        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            self.local_function ={}
            if  f.name in self.functionNameVetoList:
                continue
            #print(f.name)
            self.parent = parent
            self.FuncArgs = list()
            self.LocalVar = list()
            self.Archetecture_vars =[]
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
                header += x.hdl_conversion__._vhdl__DefineSymbol(x, "variable")

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
            
    
    def extractFunctionsForClass_impl(self, ClassInstance,parent, funcDef, FuncArgs , setDefault = False ):
            self.push_scope("function")
            for x in FuncArgs:
                if x["symbol"] == None:
                    return None

            ClassName  = type(ClassInstance).__name__
            self.parent = parent
            self.FuncArgs = FuncArgs
            self.LocalVar = list()
            self.Archetecture_vars =[]
            FuncArgsLocal = copy.copy(FuncArgs)
            varSigSuffix = "_"
            for x in FuncArgsLocal:
                if x["symbol"].varSigConst == varSig.signal_t:
                    varSigSuffix += "1"
                else:
                    varSigSuffix += "0"


            body = self.Unfold_body(funcDef)

            bodystr= str(body)
            print("----------" , funcDef.name)
            argList = [x["symbol"].to_arglist(x['name'],ClassName, withDefault = setDefault and  (x["name"] != "self")) for x in FuncArgsLocal]
            ArglistProcedure = join_str(argList,Delimeter="; ")
            

         
            
            if "return" in bodystr:
                ArglistProcedure = ArglistProcedure.replace(" in "," ").replace(" out "," ").replace(" inout "," ")
                ret = v_function(
                    name=funcDef.name+varSigSuffix, 
                    body=bodystr,
                    VariableList=self.get_local_var_def(), 
                    returnType=body.get_type(),
                    argumentList=ArglistProcedure,
                    isFreeFunction=True
                )
            else:
                ret = v_procedure(
                    name=funcDef.name+varSigSuffix,
                    body=bodystr,
                    VariableList=self.get_local_var_def(), 
                    argumentList=ArglistProcedure,
                    isFreeFunction=True
                )
            self.pop_scope()
            return ret

    def extractArchetectureForClass(self,ClassInstance,Arc):
        ret = None
        ClassInstance = copy.deepcopy(ClassInstance)
        self.local_function ={}
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.Archetecture_vars =[]
        self.FuncArgs.append(
                {
                    "name":"self",
                    "symbol":  ClassInstance,
                    "ScopeType": InOut_t.InOut_tt

                }
        )
            #p=ClassInstance._process1()
            
            #self.local_function = p.__globals__
        self.local_function = ClassInstance.__init__.__globals__
        ClassInstance.vhdl_name = "!!SELF!!"
#        self.Archetecture_vars = ClassInstance.__local_symbols__
        body = self.Unfold_body(Arc)  ## get local vars 

        if self.Missing_template == True:
            ClassInstance.hdl_conversion__.FlagFor_TemplateMissing(ClassInstance)
            ClassInstance.hdl_conversion__.MissingTemplate = True

        else:
            ret = v_Arch(body=body,Symbols=self.LocalVar, Arch_vars=self.Archetecture_vars,ports=ClassInstance.getMember())

        self.local_function ={}
        self.FuncArgs = list()
        self.LocalVar = list()
        self.Archetecture_vars =[]
        return ret

      
    #@profile
    def extractFunctionsForClass(self,ClassInstance,parent ):
        t = time.time()
        index = 0
        fun_ret = []
        primary = ClassInstance.hdl_conversion__.get_primary_object(ClassInstance)
        ClassInstance.hdl_conversion__ = primary.hdl_conversion__
        ClassInstance.hdl_conversion__.MissingTemplate = False
        ClassName  = type(ClassInstance).__name__
        ClassInstance_local = v_deepcopy(ClassInstance)
        #ClassInstance_local._remove_connections()
        
        cl = self.getClassByName(ClassName)
        print("processing ", ClassName, " MemfunctionCalls ",len(ClassInstance.hdl_conversion__.MemfunctionCalls))
        for f in cl.body:
            index += 1000
            if  f.name in self.functionNameVetoList:
                continue
            
            if f.decorator_list and f.decorator_list[0].id == 'architecture' :
                if f.name not in [x["name"] for x in ClassInstance.hdl_conversion__.archetecture_list ]:
                    arc = self.extractArchetectureForClass(ClassInstance,f)
                    if arc:
                        ClassInstance.hdl_conversion__.archetecture_list.append({
                        "name"   : f.name,
                        "symbol" : arc
                        })
                    #fun_ret.append(arc)
                        pass
                continue
            print("start create function for template", f.name)
            #print(ClassInstance.hdl_conversion__.MemfunctionCalls)

            ArglistLocal = []
            ClassInstance.set_vhdl_name ( "self",True)
            ClassInstance.Inout  = InOut_t.InOut_tt
            Arglist = []
            Arglist.append(
                {
                    "name":"self",
                    "symbol": v_deepcopy(ClassInstance),
                    "ScopeType": InOut_t.InOut_tt

                }
            )
            Arglist += list(self.get_func_args_list(f))

            exist = checkIfFunctionexists(ClassInstance,f.name , Arglist)
            if exist == False:
                print("is new Function", f.name)
                len_Arglist = len(Arglist)

                if len(ArglistLocal) == 0:

                    ArglistLocal.append(
                    {
                        "name":"self",
                        "symbol": v_deepcopy(ClassInstance),
                        "ScopeType": InOut_t.InOut_tt

                    }
                    )

                    ArglistLocal += list(self.get_func_args_list(f))
                

                ClassInstance.hdl_conversion__.MemfunctionCalls.append(
                        {
                            "name" : f.name,
                            "args":  [x["symbol"] for x in   Arglist[0:len_Arglist]],
                            "self" :v_deepcopy(ClassInstance),
                            "call_func" : None,
                            "func_args" : None,
                            "setDefault" : True
                        }
                    )

            
            

        for temp in ClassInstance.hdl_conversion__.MemfunctionCalls:
            if temp["call_func"] != None:
                continue
                
                
            index += 1
            ArglistLocal = []
            ArglistLocal.append({
                        "name":"self",
                        "symbol": v_deepcopy(ClassInstance),
                        "ScopeType": InOut_t.InOut_tt

            })
            f = [x for x in  cl.body if x.name == temp["name"]]
            ArglistLocal += list(self.get_func_args_list(f[0]))
            newArglist = GetNewArgList(f[0].name, ArglistLocal, temp)

            if newArglist != None:
                print("is new template", f[0].name)
                index += 100000
                ret = self.extractFunctionsForClass_impl(ClassInstance_local, parent, f[0], newArglist , temp["setDefault"]  )
                temp["call_func"] = call_func
                temp["func_args"] = newArglist[0: len(ArglistLocal)] #deepcopy
                print("end create function for template ",f[0].name)
                if ret:
                    fun_ret.append( ret )
        
        elapsed = time.time() - t
        print ("extractFunctionsForClass", elapsed ,index)      
        return fun_ret

    def Unfold_body(self,FuncDef):
        ftype = type(FuncDef).__name__
        return self._Unfold_body[ftype](self,FuncDef)

    def unfold_argList(self,x):
        x_type = type(x).__name__
        if x_type in self._unfold_argList:
            return self._unfold_argList[x_type](self, x)
        return self._Unfold_body[x_type](self,x)

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
                    self.LocalVar.append(y)
                    return y

        if self.parent:
            ret = self.parent.getInstantByName(SymbolName)
            if ret:
                return ret 
                
        try: 
            return self.local_function[SymbolName]
        except:
            pass
        
        for x in self.Archetecture_vars:
            if x["name"] == SymbolName:
                self.LocalVar.append(x["symbol"])
                return x["symbol"]

        raise Exception("Unable to find symbol", SymbolName, "\nAvalible Symbols\n",self.FuncArgs)





    def get_func_args(self, funcDef):
        

        for i in range(len(funcDef.args.args),1,-1):
            try:
                default = funcDef.args.defaults[i-2]
            except:
                default = None
            yield (funcDef.args.args[i-1].arg,default)

    def get_func_args_list(self, funcDef):
        
    
        for args in self.get_func_args(funcDef): 
            inArg = None
            if args[1] != None:
                inArg = self.unfold_argList(args[1])
                inArg = to_v_object(inArg)
                inArg.set_vhdl_name(args[0],True)
            yield {
                    "name": args[0],
                    "symbol": inArg
                }

def call_func(obj, name, args, astParser=None,func_args=None):
    varSigSuffix = "_"
    for x in func_args:
        if get_symbol(x).varSigConst == varSig.signal_t:
            varSigSuffix += "1"
        else:
            varSigSuffix += "0"
    ret = []

    for x in range(len(args)):
        ys =func_args[x]["symbol"].hdl_conversion__.extract_conversion_types(func_args[x]["symbol"])
        for y in ys:
            line = func_args[x]["name"] + y["suffix"]+ " => " + args[x].vhdl_name + y["suffix"]
            ret.append(line)
            if y["symbol"].varSigConst ==varSig.signal_t:
                members = y["symbol"].getMember()
                for m in members:
                    if m["symbol"]._writtenRead == InOut_t.output_t:
                        line = func_args[x]["name"] + y["suffix"]+"_"+ m["name"] +" => " + args[x].vhdl_name + y["suffix"]  +"."+m["name"]
                        ret.append(line)
                        #print(line)
            



    ret = join_str(ret, Delimeter=", ", start= name + varSigSuffix +"(" ,end=")")
    #print(ret)
    return ret