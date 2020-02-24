from enum import Enum 
import copy
import  inspect 


def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()

def file_set_content(filename,content):
    with open(filename,'w') as f:
        f.write(content)

def raise_if(condition,errorMessage):
    if condition:
        raise Exception(errorMessage)


def get_value_or_default(value,default):
    if value == None:
        return default

    return value

def add_symbols_to_entiy():
    funcrec = inspect.stack()
    for x in funcrec:
            #print (x.function)
        if x.function == "architecture":
            f_locals = x.frame.f_locals
            for y in f_locals:
                if y != "self" and issubclass(type(f_locals[y]), vhdl_base0):
                    f_locals["self"]._add_symbol(y,f_locals[y])
                    print(y)


__VHDL__OPS_to2str= {
"Gt": ">",
"Eq" : "=",
"GtE" :">=",
"LtE" :"<=",
"Lt"  :"<"
}
def ops2str(ops):
    return  __VHDL__OPS_to2str[ops]
        
    raise Exception("unable to find Binary Operator")


gStatus = {
    "isConverting2VHDL" : False,
    "isProcess" : False
}

def isConverting2VHDL():
    return gStatus["isConverting2VHDL"]

def set_isConverting2VHDL(newStatus):
    gStatus["isConverting2VHDL"] = newStatus

def isProcess():
    return gStatus["isProcess"]

def set_isProcess(newStatus):
    gStatus["isProcess"] = newStatus



gHDL_objectList = []


        

def make_unique_includes(incs,exclude=None):
    sp = incs.split(";")
    sp  = [x.strip() for x in sp]
    sp = sorted(set(sp))
    ret = ""
    for x in sp:
        if len(x)==0:
            continue
        if exclude and "work."+exclude+".all" in x:
            continue
        ret += x+";\n"
    return ret



    
    

class vhdl_converter_base:

    def convert_all(self, obj, ouputFolder):
        FilesDone = ['']

        for x in gHDL_objectList:
            packetName =  x.hdl_conversion__.get_packet_file_name(x)
            if packetName not in FilesDone:
                packet = x.hdl_conversion__.get_packet_file_content(x)
                if packet:
                    file_set_content(ouputFolder+"/" +packetName,packet)
                FilesDone.append(packetName)
            
            entiyFileName =  x.hdl_conversion__.get_entity_file_name(x)

            if entiyFileName not in FilesDone:
                entity_content = x.hdl_conversion__.get_enity_file_content(x)
                if entity_content:
                    file_set_content(ouputFolder+"/" +entiyFileName,entity_content)
                FilesDone.append(entiyFileName)

    def get_packet_file_name(self, obj):
        return ""

    def get_packet_file_content(self, obj):
        return ""

    def get_enity_file_content(self, obj):
        return ""

    def get_entity_file_name(self, obj):
        return ""

    def get_type_simple(self,obj):
        return type(obj).__name__

    def parse_file(self,obj):
        return ""

    def includes(self,obj, name,parent):
        return ""

    def recordMember(self,obj, name,parent,Inout=None):
        return ""

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        return "" 

    def getHeader(self,obj, name,parent):
        return ""
    def getFuncArg(self,obj,name,parent):
        return ""

    def getBody(self,obj, name,parent):
        return ""

    def _vhdl_make_port(self, obj, name):
        objName = str(obj)
        if obj.__Driver__ != None:
            objName = str(obj.__Driver__)

        return  name + " => " + objName


    def _vhdl_get_attribute(self,obj, attName):
        return str(obj) + "." +str(attName)

    def _vhdl_slice(self,obj, sl,astParser=None):
        raise Exception("Not implemented")
        return obj
    
    def _vhdl__compare(self,obj, ops, rhs):
        return str(obj) + " " +ops2str(ops)+" " + str(rhs)

    def _vhdl__add(self,obj,args):
        return str(obj) + " + " + str(args)

    def _vhdl__to_bool(self,obj, astParser):
        return "pyhdl_to_bool(" + str(obj) + ") "

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):
        return obj

    def _vhdl__reasign_type(self, obj ):
        return obj

    def _vhdl__reasign(self, obj, rhs, context=None):
        return str(obj) + " := " +  str(rhs)

    def _vhdl__call_member_func(self, obj, name, args):
        if name =="Connect":
            return str(obj)
        return name+"(" +  str(obj) + ")" 

    

    def _vhdl__DefineSymbol(self,obj, VarSymb="variable"):
        print("_vhdl__DefineSymbol is deprecated")
        return VarSymb +" " +str(obj) + " : " +obj.type +" := " + obj.type+"_null;\n"
        #return " -- No Generic symbol definition for object " + self.getName()

    def get_architecture_header(self, obj):
        if obj.Inout != InOut_t.Internal_t:
            return ""
        
        if obj.varSigConst != varSig.signal_t or obj.varSigConst != varSig.signal_t:
            return ""

        VarSymb = get_varSig(obj.varSigConst)

        return VarSymb +" " +str(obj) + " : " +obj.type +" := " + obj.type+"_null;\n"
        
    def get_architecture_body(self, obj):
        return ""

    def get_packet_definition(self, obj):
        return ""

    def get_entity_definition(self, obj):
        return ""

    def get_port_list(self,obj):
        return ""

    def get_process_header(self,obj):
        if obj.Inout != InOut_t.Internal_t:
            return ""
        
        if obj.varSigConst != varSig.variable_t:
            return ""

        VarSymb = get_varSig(obj.varSigConst)

        return VarSymb +" " +str(obj) + " : " +obj.type +" := " + obj.DefaultValue +";\n"



    def _vhdl__Pull(self,obj):
        return ""

    def _vhdl__push(self,obj):
        return ""

    def get_assiment_op(self, obj):
        varSigConst = obj.varSigConst
        raise_if(varSigConst== varSig.const_t, "cannot asign to constant")

        if varSigConst== varSig.signal_t:
            asOp = " <= "
        else: 
            asOp = " := "

        return asOp

    def InOut_t2str(self, obj):
        inOut = obj.Inout
        if inOut == InOut_t.input_t:
            return " in "
        elif inOut == InOut_t.output_t:
            return " out "

        raise Exception("unkown Inout type",inOut)

    def get_default_value(self,obj):
        return obj.type + "_null"


    def extract_conversion_types(self, obj):
        return [{ "suffix":"", "symbol": obj}]

    def get_Name_array(self,obj):
        return obj.hdl_conversion__.get_type_simple(obj)+"_a"
class vhdl_base0:
    def __init__(self):
        super().__init__()
        gHDL_objectList.append(self)
        self._isInstance = False
        self.hdl_conversion__ = vhdl_converter_base()
    
    
    def set_simulation_param(self,module, name,writer):
        pass


    def _sim_set_push_pull(self, symbol):
            
            if hasattr(self, "_onPull"):
                symbol._sim_append_Pull_update_list( getattr(self, '_onPull'))

            if hasattr(self, "_onPush"):
                symbol._sim_append_Push_update_list(getattr(self, '_onPush'))



    def _sim_append_update_list(self,up):
        raise Exception("update not implemented")

    def _get_Stream_input(self):
        raise Exception("update not implemented")

    def _get_Stream_output(self):
        raise Exception("update not implemented")

class vhdl_base(vhdl_base0):

    def __init__(self):
        super().__init__()
        


    def getName(self):
        return type(self).__name__

    def to_arglist(self,name,parent):
        
        localname = self.vhdl_name
        if name:
            localname = name

        
        return localname +" : " +self.type
    
    def set_varSigConst(self, varSigConst):
        raise Exception("not implemented")

    def get_vhdl_name(self,Inout):
        return None
        
    def isInOutType(self,Inout):
        return False
        
    def getVMember(self):
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            print(type(t).__name__)
            if issubclass(type(t),vhdl_base):
                yield t, x[0]
            elif type(t).__name__ == "EnumMeta":
                yield v_enum(t), x[0]



  





    def _connect(self,rhs):
        raise Exception("not implemented")
    


    def _sim_get_value(self):
        raise Exception("not implemented")


def optional_concatonat(first, delimer, Second):
    if first and Second:
        return first + delimer +Second
    
    return first + Second

def value(Input):
    if issubclass(type(Input), vhdl_base):
        return Input._sim_get_value()
    
    if type(Input).__name__ == "v_Num":
        return Input.value

    return Input

class  InOut_t(Enum):
    input_t    = 1
    output_t   = 2    
    Internal_t = 3
    Master_t   = 4
    Slave_t    = 5
    InOut_tt   = 6
    Default_t  = 7

class varSig(Enum):
    variable_t = 1
    signal_t =2 
    const_t =3

v_defaults ={
"defVarSig" : varSig.variable_t
}


def getDefaultVarSig():
    return v_defaults["defVarSig"]

def setDefaultVarSig(new_defVarSig):
    v_defaults["defVarSig"] = new_defVarSig

def get_varSig(varSigConst):
    if varSigConst == varSig.signal_t:
        return "signal"
    elif varSigConst == varSig.variable_t:
        return  "variable"

    raise Exception("unknown type")





def InoutFlip(inOut):
    if inOut == InOut_t.input_t:
        return InOut_t.output_t
    elif inOut ==   InOut_t.output_t:
        return InOut_t.input_t
    elif inOut == InOut_t.Master_t:
        return InOut_t.Slave_t
    
    elif inOut == InOut_t.Slave_t:
        return InOut_t.Master_t

    else:
        return inOut

class v_classType_t(Enum):
    transition_t = 1
    Master_t = 2
    Slave_t = 3
    Record_t =4


def v_variable(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.variable_t)
    return ret
    
    
def v_signal(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.signal_t)
    return ret
    
def port_out(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(getDefaultVarSig())
    return ret

def variable_port_out(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(varSig.variable_t)
    return ret

def port_in(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(getDefaultVarSig())
    return ret

def variable_port_in(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(varSig.variable_t)
    return ret

def port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(getDefaultVarSig())
    return ret

def variable_port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.variable_t)
    return ret

def signal_port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.signal_t)
    return ret

def port_Stream_Master(symbol):
    ret = port_Master(symbol)
    ret._isInstance = False
    funcrec = inspect.stack()[1]
        
    f_locals = funcrec.frame.f_locals

    raise_if(f_locals["self"]._StreamOut != None, "the _StreamOut is already set")
 
    f_locals["self"]._StreamOut = ret
                    
    return ret 

def signal_port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.signal_t)
    return ret


def port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(getDefaultVarSig())
    return ret

def variable_port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.variable_t)
    return ret

def port_Stream_Slave(symbol):
    ret = port_Slave(symbol)
    ret._isInstance = False
    funcrec = inspect.stack()[1]
        
    f_locals = funcrec.frame.f_locals
    raise_if(f_locals["self"]._StreamIn != None, "the _StreamIn is already set")
    
    f_locals["self"]._StreamIn = ret
                    
    return ret 
def v_copy(symbol,varSig=None):
    ret= copy.deepcopy(symbol)
    ret.setInout(InOut_t.Internal_t)
    ret._isInstance = False
    ret.vhdl_name = None
    if varSig == None:
        ret.set_varSigConst(getDefaultVarSig())
    return ret

def port(symbol):
    if issubclass(type(symbol),v_class):
        if symbol.__v_classType__ == v_classType_t.Master_t:

            symbol.setInout(InOut_t.Master_t)
        elif symbol.__v_classType__ == v_classType_t.Slave_t:

            symbol.setInout(InOut_t.Slave_t)
        
        else:
            raise Exception("Unexpected class type " , symbol.__v_classType__)

            
        return symbol
    else:
        raise Exception("Unexpected type " , type(symbol))


