
import copy

from .xgenBase import *
from .xgen_v_enum import * 
from .xgen_to_v_object import *
#from .xgen_v_entity import *

def Node_line_col_2_str(astParser, Node):
    return  "Error in File: "+ astParser.sourceFileName+" line: "+str(Node.lineno) + ".\n"


def unfold_Str(astParser, strNode):
    return strNode.s
def unfold_num(astParser, NumNode):
    return NumNode.n


def Unfold_call(astParser, callNode):
        
    return astParser._unfold_symbol_fun_arg[callNode.func.id](astParser, callNode.args)


class GNames:
    process = "process"


class indent:
    def __init__(self):
        self.ind = 2

    def inc(self):
        self.ind += 2
    
    def deinc(self):
        self.ind -= 2

    def __str__(self):
        ret  = ''.ljust(self.ind)
        return ret

gIndent = indent()


def port_in_to_vhdl(astParser,Node,Keywords=None):
    return port_in(astParser.unfold_argList(Node[0]) )

def port_out_to_vhdl(astParser,Node,Keywords=None):
    return port_out(astParser.unfold_argList(Node[0]) )

def variable_port_in_to_vhdl(astParser,Node,Keywords=None):
    return variable_port_in(astParser.unfold_argList(Node[0]) )

def variable_port_out_to_vhdl(astParser,Node,Keywords=None):
    return  variable_port_out(astParser.unfold_argList(Node[0]) )



def v_slv_to_vhdl(astParser,Node,Keywords=None):
    args = list()
    for x in Node:
        x_obj = astParser.Unfold_body(x)
        if type(x_obj).__name__ == "v_Num":
            args.append(x_obj.value )
        else:
            args.append(x_obj)

    kwargs = {}
    for x in Keywords:
        if x.arg =='varSigConst':
            kwargs[x.arg] = astParser.Unfold_body(x.value).Value 
        else:
            kwargs[x.arg] = astParser.Unfold_body(x.value) 

    return v_slv(*args,**kwargs)


def v_sl_to_vhdl(astParser,Node,Keywords=None):
    if len(Node) == 1:
        return v_sl(InOut_t.input_t, astParser.unfold_argList(Node[0]) )
    else:
        return v_sl(InOut_t.input_t )
        
        
def v_int_to_vhdl(astParser,Node,Keywords=None):
    return v_int()


def v_bool_to_vhdl(astParser,Node,Keywords=None):
    return v_bool()
class v_ast_base:

    def __str__(self):
        return type(self).__name__

    def get_type(self):
        return ""
        
    def _vhdl__getValue(self,ReturnToObj=None,astParser=None):
        self._vhdl__setReturnType(ReturnToObj, astParser)
        return str(self)    

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        pass

class v_noop(v_ast_base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):

        return ""

class v_process_Def(v_ast_base):
    def __init__(self,BodyList,name,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
    
    def __str__(self):
        ret = "\n-----------------------------------\n" + self.name + " : process" 
        for x in self.BodyList:
            x_str =str(x) 
            sp_x_str = x_str.split("\n")[-1].strip()
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str
                if sp_x_str:
                    ret += ";"
                ret += "\n  "  

        ret += "end process"
        return ret

def body_unfold_porcess(astParser,Node, Body = None):
    localContext = astParser.Context
    astParser.push_scope(GNames.process)
    
    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    ret = list()
    astParser.Context = ret
    if Body == None:
        for x in Node.body:
            ret.append( astParser.Unfold_body(x))
    else:
        ret.append( astParser.Unfold_body(Body))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)
         
    astParser.pop_scope()

    return v_process_Def(ret,Node.name)

class v_process_body_Def(v_ast_base):
    def __init__(self,BodyList,name,LocalVar,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
        self.LocalVar = LocalVar
    
    def __str__(self):
        pull =""
        for x in self.LocalVar:
            if x.type == "undef":
                continue
            pull += x.hdl_conversion__._vhdl__Pull(x)
        push =""
        for x in self.LocalVar:
            if x.type == "undef":
                continue
            push += x.hdl_conversion__._vhdl__push(x)
        
        ret =  "("+ str(self.dec[0].argList[0])+ ") is\n"
        
        for x in self.LocalVar:
            ret += x.hdl_conversion__.get_process_header(x)
        ret += "begin\n  " 
        ret += "if " + self.dec[0].name +"(" + str(self.dec[0].argList[0])+") then \n"
        ret += pull
        for x in self.BodyList:
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "
        ret += push
        ret += "end if;\n"
        return ret

def body_unfold_porcess_body(astParser,Node):
    if astParser.get_scope_name() != GNames.process:
        return body_unfold_porcess(astParser,Node = Node ,Body = Node)
    localContext = astParser.Context
    

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)

    return v_process_body_Def(ret,Node.name,astParser.LocalVar,decorator_l)


class v_process_body_timed_Def(v_ast_base):
    def __init__(self,BodyList,name,LocalVar,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
        self.LocalVar = LocalVar
    
    def __str__(self):
        pull =""
        for x in self.LocalVar:
            if x.type == "undef":
                continue
            pull += x.hdl_conversion__._vhdl__Pull(x)
        push =""
        for x in self.LocalVar:
            if x.type == "undef":
                continue
            push += x.hdl_conversion__._vhdl__push(x)
        
        ret =  "\n"
        
        for x in self.LocalVar:
            ret += x.hdl_conversion__._vhdl__DefineSymbol(x, "variable")
        ret += "begin\n  " 
        
        ret += pull
        for x in self.BodyList:
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "
        ret += push

        return ret

def body_unfold_porcess_body_timed(astParser,Node):
    
    if astParser.get_scope_name() != GNames.process:
        return body_unfold_porcess(astParser,Node = Node ,Body = Node)

    localContext = astParser.Context
    

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)

    return v_process_body_timed_Def(ret,Node.name,astParser.LocalVar,decorator_l)

class porcess_combinational(v_ast_base):
    def __init__(self, Name, BodyList):
        self.Name =Name
        self.Body = BodyList

    def __str__(self):
        ret = "  -- begin " + self.Name +"\n"
        
        for x in self.Body:
            ret += "  " + str(x) + ";\n"
        ret += "  -- end " + self.Name 
        return ret

def body_unfold_porcess_body_combinational(astParser,Node):
    
    localContext = astParser.Context
    astParser.push_scope(GNames.process)

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.signal_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)
    
    astParser.pop_scope()

    return porcess_combinational(Node.name, ret)

class v_funDef(v_ast_base):
    def __init__(self,BodyList,dec=None):
        self.BodyList=BodyList
        self.dec = dec

    def __str__(self):
        ret = "" 
        for x in self.BodyList:
            if x == None:
                continue 
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "

        return ret

    def get_type(self):
        for x in self.BodyList:
            if type(x).__name__ == "v_return":
                return x.get_type()
    



def body_unfold_functionDef(astParser,Node):
    astParser.FuncArgs.append(
                   {
                    "name":Node.name,
                    "symbol": Node.name,
                    "ScopeType": ""

                }
    )
    if len(Node.decorator_list) == 1 and Node.decorator_list[0].func.id== "process":
        return body_unfold_porcess(astParser,Node)
    elif len(Node.decorator_list) == 1 and Node.decorator_list[0].func.id== "rising_edge":
        return body_unfold_porcess_body(astParser,Node)

    elif len(Node.decorator_list) == 1 and Node.decorator_list[0].func.id== "timed":
        return body_unfold_porcess_body_timed(astParser,Node)

    elif len(Node.decorator_list) == 1 and Node.decorator_list[0].func.id== "combinational":
        return body_unfold_porcess_body_combinational(astParser,Node)


    decorator_l = astParser.Unfold_body(Node.decorator_list)
    localContext = astParser.Context

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    return v_funDef(ret,decorator_l)



class v_return (v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return "return "  + str(self.value) 
    
    def get_type(self):
        ty =  self.value.get_type()
        if "std_logic_vector" in ty:
            return "std_logic_vector"
        return ty

def body_unfold_return(astParser,Node):
    return v_return(astParser.Unfold_body(Node.value) )

class v_compare(v_ast_base):
    def __init__(self,lhs,ops,rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.ops = ops

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs.hdl_conversion__._vhdl__compare(self.lhs, self.ops, self.rhs)
        
        return  str(self.lhs)  + " = " +   str(self.rhs) 

    def get_type(self):
        return "boolean"

    def _vhdl__to_bool(self,astParser):
        if type(self.rhs).__name__ == "v_name":
            rhs = astParser.get_variable(self.rhs.Value,None)
        else:
            rhs = self.rhs

        if type(self.lhs).__name__ == "v_name":
            obj = astParser.get_variable(self.lhs.Value,None)
            return obj.hdl_conversion__._vhdl__compare(obj, rhs)

        elif issubclass(type(self.lhs),v_class):
            return self.lhs.hdl_conversion__._vhdl__compare(self.lhs,self.ops, self.rhs)
        
        elif issubclass(type(self.lhs),v_symbol):
            return self.lhs.hdl_conversion__._vhdl__compare(self.lhs, self.ops ,self.rhs)

        elif issubclass(type(self.lhs),v_enum):
            return self.lhs.hdl_conversion__._vhdl__compare(self.lhs, self.ops ,self.rhs)
        
        raise Exception("unknown type",type(self.lhs).__name__ )

def body_unfold_Compare(astParser,Node):
    if len (Node.ops)>1:
        raise Exception("unexpected number of operators")
    return v_compare( astParser.Unfold_body(Node.left),type(Node.ops[0]).__name__,  astParser.Unfold_body(Node.comparators[0] ) )

class v_Attribute(v_ast_base):
    def __init__(self,Attribute,Obj):
        self.obj = Obj 
        self.att = getattr(self.obj["symbol"],Attribute)
        self.att.set_vhdl_name(self.obj["symbol"].vhdl_name+"."+Attribute)
        self.Attribute = Attribute

    def __str__(self):
        return str(self.obj) +"." + str(self.Attribute)

def body_unfold_Attribute(astParser,Node):
    val = astParser.Unfold_body(Node.value)
    
    if type(val).__name__ == "str":

        obj=astParser.getInstantByName(val)
    else:
        obj = val 
    if issubclass(type(obj),v_enum):
        return v_enum(getattr(obj.type,Node.attr))
    att = getattr(obj,Node.attr)
    
    if type(type(att)).__name__ == "EnumMeta": 
        return v_enum(att)
    

    n = obj.hdl_conversion__._vhdl_get_attribute(obj,Node.attr)

    att.set_vhdl_name(n)
    
    astParser.FuncArgs.append(
                    {
                    "name":att.vhdl_name,
                    "symbol": att,
                    "ScopeType": obj.Inout

                })
    return att
    
class v_Num(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "integer"

    def _vhdl__getValue(self,ReturnToObj=None,astParser=None):
        if ReturnToObj.type =="std_logic":
            return  "'" + str(self.value)+ "'"
        if  "std_logic_vector" in ReturnToObj.type:
            if str(self) == '0':
                return " (others => '0')"
            
            return  """std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=str(ReturnToObj),
                    src = str(self.value)
            )

        if ReturnToObj.type =="integer":
            return  str(self.value)
            
        return "convert2"+ ReturnToObj.get_type().replace(" ","") + "(" + str(self) +")"
        
def body_unfold_Num(astParser,Node):
    return v_Num(Node.n)

class v_Str(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "str"

def body_unfold_str(astParser,Node):
    return v_Str(Node.s)

class v_variable_cration(v_ast_base):
    def __init__(self,rhs,lhs):
        self.rhs = rhs
        self.lhs = lhs



    def __str__(self):
        #return str(self.lhs.vhdl_name) +" := "+ str(self.lhs.get_value()) 
        self.lhs.vhdl_name = self.rhs
        return self.lhs.hdl_conversion__.get_architecture_body(self.lhs)



    def get_type(self):
        return None

def  body_unfold_assign(astParser,Node):
    if len(Node.targets)>1:
        raise Exception(Node_line_col_2_str(astParser, Node)+"Multible Targets are not supported")

    for x in astParser.LocalVar:
        if Node.targets[0].id in x.vhdl_name:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")

    for x in astParser.FuncArgs:
        if Node.targets[0].id == x["name"]:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")
            


    if type(Node.targets[0]).__name__ != "Name":
        raise Exception(Node_line_col_2_str(astParser, Node)+" unknown type")
    
    lhs = v_name (Node.targets[0].id)
    rhs =  astParser.Unfold_body(Node.value)
    rhs =  to_v_object(rhs)
    rhs.set_vhdl_name(lhs.Value)
    astParser.LocalVar.append(rhs)
    return v_variable_cration( lhs,  rhs)


class v_name(v_ast_base):
    def __init__(self,Value):
        self.Value = Value

        

    def __str__(self):
        return str(self.Value)


    



def  body_unfold_Name(astParser,Node):
    ret = astParser.getInstantByName(Node.id)
    return ret

def handle_print(astParser,args,keywords=None):
    return v_noop()

class handle_v_switch_cl(v_ast_base):
    def __init__(self,Default, cases):
        self.Default = Default
        self.cases = cases
        self.ReturnToObj = None

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        self.ReturnToObj = ReturnToObj
        for x in self.cases:
            x._vhdl__setReturnType(ReturnToObj, astParser)



    def __str__(self):
        ret = "\n    " 
        for x in self.cases:
            x = x._vhdl__getValue(self.ReturnToObj)
            ret += str(x)
        default = self.Default._vhdl__getValue(self.ReturnToObj)
        
        ret += str(default)
        return ret

def handle_v_switch(astParser,args,keywords=None):
    body = list()
    for x in args[1].elts:
        body.append(astParser.Unfold_body(x))

    return handle_v_switch_cl(astParser.Unfold_body(args[0]),body)


class handle_v_case_cl(v_ast_base):
    def __init__(self, value,pred):
        self.value = value
        self.pred = pred 

    def __str__(self):
        
        ret = str(self.value) + " when " + str(self.pred) + " else\n    "
        return ret

def handle_v_case(astParser,args,keywords=None):
    test =v_type_to_bool(astParser,astParser.Unfold_body(args[0]))
    return handle_v_case_cl(astParser.Unfold_body(args[1]), test)

class v_call(v_ast_base):
    def __init__(self,memFunc, symbol, vhdl):
        self.memFunc = memFunc    
        self.symbol  =  symbol
        
        self.vhdl =vhdl
    
    def __str__(self):
        return str(self.vhdl) 
    
    def get_type(self):
        return self.symbol.type

def body_unfold_call_local_func(astParser,Node):

    args = list()
    for x in Node.args:
        args.append(astParser.Unfold_body(x))

    kwargs = {}
    for x in Node.keywords:
        kwargs[x.arg] = astParser.Unfold_body(x.value) 
    return astParser.local_function[Node.func.id](*args,**kwargs)

    if len(Node.args) == 0:
        return astParser.local_function[Node.func.id]()
    elif len(Node.args) == 1:
        return astParser.local_function[Node.func.id](astParser.Unfold_body(Node.args[0]))
    elif len(Node.args) == 2:
        return astParser.local_function[Node.func.id](astParser.Unfold_body(Node.args[0]),astParser.Unfold_body(Node.args[1]))

def body_unfold_call(astParser,Node):
    if hasattr(Node.func, 'id'):
        if Node.func.id in astParser._unfold_symbol_fun_arg:
            return astParser._unfold_symbol_fun_arg[Node.func.id](astParser, Node.args,Node.keywords)
        elif Node.func.id in astParser.local_function:
            return body_unfold_call_local_func( astParser ,Node)
        else:
            raise Exception("unknown function")

    elif hasattr(Node.func, 'value'):
        obj = astParser.getInstantByName(Node.func.value.id)
        memFunc = Node.func.attr
        f = getattr(obj,memFunc)

        args = list()
        for x in Node.args:
            pass #fill arg list here 
        
        if len(Node.args) == 0:
            r = f()  # find out how to forward args 
        elif len(Node.args) == 1:
            r = f(astParser.Unfold_body(Node.args[0]))  # find out how to forward args
        elif len(Node.args) == 2:
            r = f(astParser.Unfold_body(Node.args[0]),astParser.Unfold_body(Node.args[1]))  # find out how to forward args
        

        r = to_v_object(r)
        vhdl = obj.hdl_conversion__._vhdl__call_member_func(obj, memFunc,args)
        r.set_vhdl_name(vhdl)
        ret = v_call(memFunc,r, vhdl)
        return ret

    elif hasattr(Node.func, 'func'):
        return body_unfold_call(astParser,Node.func)


    raise Exception("Unknown call type")





def body_expr(astParser,Node):
    return    astParser.Unfold_body(Node.value)


def body_RShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),vhdl_base):
        rhs = rhs.hdl_conversion__._vhdl__reasign_type(rhs)
        lhs = lhs._vhdl__getValue(lhs,astParser)
        lhs >> rhs
        return v_re_assigne(rhs, lhs)

    var = astParser.get_variable(rhs.Value, Node)

    return v_re_assigne(lhs, var)


class v_re_assigne(v_ast_base):
    def __init__(self,lhs, rhs,context=None):
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        

 

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs.hdl_conversion__._vhdl__reasign(self.lhs, self.rhs)

        return str(self.lhs) + " := " +  str(self.rhs) 

def body_LShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),vhdl_base):
        lhs = lhs.hdl_conversion__._vhdl__reasign_type(lhs)
        if issubclass( type(rhs),vhdl_base):
            rhs = rhs.hdl_conversion__._vhdl__getValue(rhs, lhs,astParser)
        else:
            rhs = rhs._vhdl__getValue(lhs,astParser)

        if astParser.ContextName[-1] == 'process' and issubclass( type(rhs),vhdl_base):
            rhs.__Driver__ = 'process'

        lhs << rhs
        if astParser.ContextName[-1] == 'process':
            lhs.__Driver__ = 'process'
            
        return v_re_assigne(lhs, rhs,astParser.ContextName[-1])

    var = astParser.get_variable(lhs.Value, Node)

    return v_re_assigne(var, rhs)

class v_add(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.type = lhs.type
        

        

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs.hdl_conversion__._vhdl__add(self.lhs, self.rhs)

        return str(self.lhs) + " + " +  str(self.rhs) 

def body_add(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),vhdl_base):
        return v_add(lhs, rhs)

    var = astParser.get_variable(lhs.Value, Node)

    return v_add(var, rhs)



class v_stream_assigne(v_ast_base):
    def __init__(self,lhs, rhs,StreamOut,lhsEntity,context=None):
        self.lhsEntity = lhsEntity
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self._StreamOut =None
        if StreamOut != None:
            self._StreamOut = StreamOut

        

 

    def __str__(self):
        ret = ""
        if issubclass(type(self.lhsEntity), v_ast_base):
            ret+= str(self.lhsEntity) +";\n  "
            
        if issubclass(type(self.lhs),vhdl_base):
            ret += self.lhs.hdl_conversion__._vhdl__reasign(self.lhs, self.rhs)

        else:
            ret += str(self.lhs) + " := " +  str(self.rhs) 

        return ret


def body_bitOr(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    ret = lhs | rhs
    
    ret.astParser = astParser
            
    return ret


def body_BinOP(astParser,Node):
    optype = type(Node.op).__name__
        
    return astParser._Unfold_body[optype](astParser,Node)


class v_named_C(v_ast_base):
    def __init__(self,Value):
        self.Value = Value
        
        

        

    def __str__(self):
        return str(self.Value)



def body_Named_constant(astParser,Node):
    return v_named_C(Node.value)

def v_type_to_bool(astParser,obj):


    if type(obj).__name__ == "v_name":
        obj = astParser.get_variable(obj.Value,None)

    if type(obj).__name__ == "v_compare":
        return obj._vhdl__to_bool( astParser)

    if issubclass(type(obj),vhdl_base):
        return obj.hdl_conversion__._vhdl__to_bool(obj, astParser)

    if type(obj).__name__ == "v_call":
        return  obj.symbol._vhdl__to_bool(astParser)




    if obj.get_type() == 'boolean':
        return obj
class v_if(v_ast_base):
    def __init__(self,ifEsleIfElse, test, body,oreEsle):
        self.ifEsleIfElse = ifEsleIfElse    
        self.test=test
        self.body = body
        self.oreEsle  = oreEsle
        self.isElse = False


    def __str__(self):
        
        if self.isElse:
            gIndent.deinc()
            ret ="\n" +str(gIndent) +  "elsif ("
            gIndent.inc()
        else:
            ret ="\n" +str(gIndent) +  "if ("
        
            gIndent.inc()
        
        ret += str(self.test) +") then \n"+str(gIndent)
        for x in self.body:
            x_str =str(x)
            if x_str:
               # x_str.replace("\n","\n  ")
                ret += x_str +";\n"+str(gIndent)

        
        oreelse =""
        if len(self.oreEsle) > 0 and type(self.oreEsle[0]).__name__ != "v_if":
            gIndent.deinc()
            oreelse+="\n"+ str(gIndent) + "else"
            gIndent.inc()
            oreelse += "\n"+str(gIndent) 
            for x in self.oreEsle:
                oreelse += str(x)+";\n"+str(gIndent) 
        
        else:
            for x in self.oreEsle:
                x.isElse = True
                oreelse += str(x)
            

        ret += oreelse
        gIndent.deinc()
        if self.isElse:
            ret +=""
        else:
            ret +="\n" +str(gIndent) +  "end if" 
        

        return ret


def body_if(astParser,Node):
    
    ifEsleIfElse = "if"
    test =v_type_to_bool(astParser, astParser.Unfold_body(Node.test))
    body = astParser.Unfold_body(Node.body)
    localContext = astParser.Context
    oreEsle = list ()
    astParser.Context  = oreEsle
    for x in Node.orelse:
        oreEsle.append(astParser.Unfold_body(x))
    astParser.Context =localContext 
    return v_if(ifEsleIfElse, test, body,oreEsle)


def body_list(astParser,Node):
    localContext = astParser.Context
    ret = list()
    astParser.Context  = ret
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)
    astParser.Context =localContext 
    return ret




class v_boolOp(v_ast_base):
    def __init__(self,elements,op):
        self.elements = elements
 
        self.op = op

    def __str__(self):
        op = type(self.op).__name__
        if op == "And":
            op = " and "
        elif op == "Or":
            op = " or "
        ret = "( "
        start = ""
        for x in self.elements:
            ret += start + str(x) 
            start = op
        ret += ") "
        return ret

    def get_type(self):
        return "boolean"

    def _vhdl__to_bool(self,astParser):
        if type(self.rhs).__name__ == "v_name":
            rhs = astParser.get_variable(self.rhs.Value,None)
        else:
            rhs = self.rhs

        if type(self.lhs).__name__ == "v_name":
            obj = astParser.get_variable(self.lhs.Value,None)
            return obj.hdl_conversion__._vhdl__compare(obj, rhs)

        elif issubclass(type(self.lhs),v_class):
            return self.lhs.hdl_conversion__._vhdl__compare(self.lhs,self.rhs)


def body_BoolOp(astParser, Node):
    elements = list()
    for x in Node.values:
        e = astParser.Unfold_body(x)
        e = v_type_to_bool(astParser,e)
        elements.append(e)


    op = Node.op
    return v_boolOp(elements,op)

class v_UnaryOP(v_ast_base):
    def __init__(self,obj,op):
        self.obj = obj
        self.op = op
        self.type = "boolean"

    def __str__(self):
        op = type(self.op).__name__
        if op == "Not":
            op = " not "

        return   op +  " ( " + str(self.obj) +" ) " 

    def get_type(self):
        return "boolean"




def body_UnaryOP(astParser,Node):
    arg = astParser.Unfold_body(Node.operand)
    arg = v_type_to_bool(astParser,arg)
    #print(arg)

    return v_UnaryOP(arg, Node.op)



def body_subscript(astParser,Node):
    value = astParser.Unfold_body(Node.value)
    sl  = astParser.Unfold_body(Node.slice)
    return value.hdl_conversion__._vhdl_slice(value, sl,astParser)

def body_index(astParser,Node):
    sl  = astParser.Unfold_body(Node.value)
    return sl 

class v_decorator:
    def __init__(self,name,argList):
        self.name=name
        self.argList=argList

    def get_sensitivity_list(self):
        return str(self.argList[0])

    def get_prefix(self):
        return self.name + "(" + str(self.argList[0]) +")"

def handle_rising_edge(astParser, symb,keyword=None):
    l = list()
    for x in symb:
        s = astParser.Unfold_body(x)
        l.append(s)

    return v_decorator("rising_edge", l )


def handle_v_create(astParser, symb):
    print("asd")


class v_yield(v_ast_base):
    def __init__(self,Arg):
        self.arg = Arg

    def __str__(self):


        return   "wait for " + str(self.arg) 
        
def body_unfold_yield(astParser,Node):
    
    arg = astParser.Unfold_body(Node.value)
    return v_yield(arg)