
import copy

from .xgenBase import *
from .xgen_v_enum import * 
from .xgen_to_v_object import *

def Node_line_col_2_str(astParser, Node):
    return  "Error in File: "+ astParser.sourceFileName+" line: "+str(Node.lineno) + ".\n"



def unfold_num(astParser, NumNode):
    return NumNode.n


def Unfold_call(astParser, callNode):
        
    return astParser._unfold_symbol_fun_arg[callNode.func.id](astParser, callNode.args)




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


def port_in_to_vhdl(astParser,Node):
    return port_in(astParser.unfold_argList(Node[0]) )

def port_out_to_vhdl(astParser,Node):
    return port_out(astParser.unfold_argList(Node[0]) )

def v_slv_to_vhdl(astParser,Node):
    if len(Node) == 1:
        return v_slv(astParser.unfold_argList(Node[0]) )
    if len(Node) == 2:
        return v_slv(astParser.unfold_argList(Node[0]),astParser.unfold_argList(Node[1]))
    
    raise Exception("unexpected num of args")

def v_sl_to_vhdl(astParser,Node):
    if len(Node) == 1:
        return v_sl(InOut_t.input_t, astParser.unfold_argList(Node[0]) )
    else:
        return v_sl(InOut_t.input_t )
        
        

class v_ast_base:

    def __str__(self):
        return type(self).__name__

    def get_type(self):
        return ""


class v_funDef(v_ast_base):
    def __init__(self,BodyList):
        self.BodyList=BodyList

    def __str__(self):
        ret = "" 
        for x in self.BodyList:
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
    ret = list()
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))
    return v_funDef(ret)



class v_return (v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return "return "  + str(self.value) 
    
    def get_type(self):
        return self.value.get_type()

def body_unfold_return(astParser,Node):
    return v_return(astParser.Unfold_body(Node.value) )

class v_compare(v_ast_base):
    def __init__(self,lhs,ops,rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.ops = ops

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs._vhdl__compare(self.ops, self.rhs)
        
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
            return obj._vhdl__compare(rhs)

        elif issubclass(type(self.lhs),v_class):
            return self.lhs._vhdl__compare(self.ops, self.rhs)
        
        elif issubclass(type(self.lhs),v_symbol):
            return self.lhs._vhdl__compare(self.ops ,self.rhs)

        elif issubclass(type(self.lhs),v_enum):
            return self.lhs._vhdl__compare(self.ops ,self.rhs)
        
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
   
    obj=astParser.getInstantByName(val)
    if issubclass(type(obj),v_enum):
        return v_enum(getattr(obj.type,Node.attr))
    att = getattr(obj,Node.attr)
    
    if type(type(att)).__name__ == "EnumMeta": 
        return v_enum(att)
    
    att.set_vhdl_name(obj.vhdl_name+"."+Node.attr)

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
        return ""



    def get_type(self):
        return None

def  body_unfold_assign(astParser,Node):
    if len(Node.targets)>1:
        raise Exception(Node_line_col_2_str(astParser, Node)+"Multible Targets are not supported")

    for x in astParser.LocalVar:
        if Node.targets[0].id in x.vhdl_name:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")

    for x in astParser.FuncArgs:
        if Node.targets[0].id in x["name"]:
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




class v_call(v_ast_base):
    def __init__(self,memFunc, symbol, vhdl):
        self.memFunc = memFunc    
        self.symbol  =  symbol
        
        self.vhdl =vhdl
    
    def __str__(self):
        return str(self.vhdl) 
    
    def get_type(self):
        return self.symbol.type

def body_unfold_call(astParser,Node):
    if hasattr(Node.func, 'id'):
        return astParser._unfold_symbol_fun_arg[Node.func.id](astParser, Node.args)
    elif hasattr(Node.func, 'value'):
        obj = astParser.getInstantByName(Node.func.value.id)
        memFunc = Node.func.attr
        f = getattr(obj,memFunc)

        args = list()
        for x in Node.args:
            pass #fill arg list here 
        

        r = f()  # find out how to forward args 
        r = to_v_object(r)
        vhdl = obj._vhdl__call_member_func(memFunc,args)
        r.set_vhdl_name(vhdl)
        ret = v_call(memFunc,r, vhdl)
        return ret
    
    raise Exception("Unknown call type")





def body_expr(astParser,Node):
    return    astParser.Unfold_body(Node.value)



class v_re_assigne(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        

        

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs._vhdl__reasign(self.rhs)

        return str(self.lhs) + " := " +  str(self.rhs) 

def body_LShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),vhdl_base):
        return v_re_assigne(lhs, rhs)

    var = astParser.get_variable(lhs.Value, Node)

    return v_re_assigne(var, rhs)

class v_add(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        

        

    def __str__(self):
        if issubclass(type(self.lhs),vhdl_base):
            return self.lhs._vhdl__add(self.rhs)

        return str(self.lhs) + " + " +  str(self.rhs) 

def body_add(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),vhdl_base):
        return v_add(lhs, rhs)

    var = astParser.get_variable(lhs.Value, Node)

    return v_add(var, rhs)


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
        return obj._vhdl__to_bool(astParser)

    if issubclass(type(obj),vhdl_base):
        return obj._vhdl__to_bool(astParser)

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
    oreEsle = list ()
    for x in Node.orelse:
        oreEsle.append(astParser.Unfold_body(x))
    return v_if(ifEsleIfElse, test, body,oreEsle)


def body_list(astParser,Node):
    ret = list()
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)

    return ret




class v_boolOp(v_ast_base):
    def __init__(self,lhs,rhs,op):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def __str__(self):
        op = type(self.op).__name__
        if op == "And":
            op = " and "

        return "( " + str(self.lhs)  + op +   str(self.rhs) +")" 

    def get_type(self):
        return "boolean"

    def _vhdl__to_bool(self,astParser):
        if type(self.rhs).__name__ == "v_name":
            rhs = astParser.get_variable(self.rhs.Value,None)
        else:
            rhs = self.rhs

        if type(self.lhs).__name__ == "v_name":
            obj = astParser.get_variable(self.lhs.Value,None)
            return obj._vhdl__compare(rhs)

        elif issubclass(type(self.lhs),v_class):
            return self.lhs._vhdl__compare(self.rhs)


def body_BoolOp(astParser, Node):
    lhs = astParser.Unfold_body(Node.values[0])
    lhs = v_type_to_bool(astParser,lhs)
    rhs = astParser.Unfold_body(Node.values[1])
    rhs = v_type_to_bool(astParser,rhs)
    op = Node.op
    return v_boolOp(lhs,rhs,op)

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
    return value._vhdl_slice(sl)

def body_index(astParser,Node):
    sl  = astParser.Unfold_body(Node.value)
    return sl 
