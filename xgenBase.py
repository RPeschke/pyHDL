from enum import Enum 
import copy
import  inspect 


def architecture(func):
    def wrap(self): 
        func(self) 
    return wrap


def join_str(content, start="",end="",LineEnding="",Delimeter="",LineBeginning="", IgnoreIfEmpty=False):
    ret = ""
    if len(content) == 0 and IgnoreIfEmpty:
        return ret
    elif len(content) == 0:
        ret += start
        ret += end
        return ret

    ret += start
    
    for x in content[0:-1]:
        ret += LineBeginning + x + Delimeter + LineEnding

    ret += LineBeginning + content[-1] +  LineEnding
    ret += end
    return ret

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
                    #print(y)


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
    "isProcess" : False,
    "isPrimaryConnection" : True
}

def isConverting2VHDL():
    return gStatus["isConverting2VHDL"]

def set_isConverting2VHDL(newStatus):
    gStatus["isConverting2VHDL"] = newStatus

def isProcess():
    return gStatus["isProcess"]

def set_isProcess(newStatus):
    gStatus["isProcess"] = newStatus

def isPrimaryConnection():
    return gStatus["isPrimaryConnection"]

def set_isPrimaryConnection(newStatus):
    gStatus["isPrimaryConnection"] = newStatus

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



def get_type(symbol):
    if issubclass(type(symbol), vhdl_base0):
        return symbol.get_type()
    if symbol == None:
        return "None"
    if symbol["symbol"] == None:
        return "None"
    return symbol["symbol"].get_type()

def get_symbol(symbol):
    if issubclass(type(symbol), vhdl_base0):
        return symbol.get_symbol()
    if symbol ==None:
        return None 
    if symbol["symbol"] == None:
        return None
    return symbol["symbol"].get_symbol()
    
def isSameArgs(args1,args2, hasDefaults = False):
    if not hasDefaults and  len(args1) != len(args2):
        return False
    for i in range(len(args1)):
        if get_symbol(args1[i]) == None:
            return False
        if get_symbol(args2[i]) == None:
            return False
        if get_type(args1[i]) != get_type( args2[i]):
            return False
        if get_symbol(args1[i]).varSigConst != get_symbol(args2[i]).varSigConst:
            return False
    return True  
class vhdl_converter_base:

    def __init__(self):
        self.MemfunctionCalls=[]
        self.IsConverted = False
        self.MissingTemplate = False

    def FlagFor_TemplateMissing(self, obj):
        primary = obj.hdl_conversion__.get_primary_object(obj)
        primary.hdl_conversion__.MissingTemplate  = True

    def reset_TemplateMissing(self, obj):
        primary = obj.hdl_conversion__.get_primary_object(obj)
        primary.hdl_conversion__.MissingTemplate  = False  

    def isTemplateMissing(self,obj):
        primary = obj.hdl_conversion__.get_primary_object(obj)
        return primary.hdl_conversion__.MissingTemplate  == True  

    def IsSucessfullConverted(self,obj):
        if obj.hdl_conversion__.isTemplateMissing(obj):
            return False
        return self.IsConverted

    def convert_all(self, obj, ouputFolder):

        
        
        FilesDone = ['']
        while len(FilesDone) > 0:
            FilesDone = []
            print("==================")
            for x in gHDL_objectList:
                if "axis"  in type(x).__name__ :
                    #print("axi")
                    pass
                #print("----------------")
                
                if x.hdl_conversion__.IsSucessfullConverted(x):
                    continue
                

                packetName =  x.hdl_conversion__.get_packet_file_name(x)
                if packetName not in FilesDone:
                    print("<"+type(x).__name__ +">")
                    x.hdl_conversion__.reset_TemplateMissing(x)
                    packet = x.hdl_conversion__.get_packet_file_content(x)
                    if packet:
                        file_set_content(ouputFolder+"/" +packetName,packet)
                    FilesDone.append(packetName)
                    print("</"+ type(x).__name__, x.hdl_conversion__.MissingTemplate, ">")
                    #print(type(x).__name__)
                    #print("processing")
                    
                
                entiyFileName =  x.hdl_conversion__.get_entity_file_name(x)

                if entiyFileName not in FilesDone:
                    print("<"+type(x).__name__ +">")
                    x.hdl_conversion__.reset_TemplateMissing(x)
                    entity_content = x.hdl_conversion__.get_enity_file_content(x)
                    if entity_content:
                        file_set_content(ouputFolder+"/" +entiyFileName,entity_content)
                    FilesDone.append(entiyFileName)
                    print("</"+ type(x).__name__, x.hdl_conversion__.MissingTemplate, ">")
                    #print("processing")
                
                x.hdl_conversion__.IsConverted = True

    def get_primary_object(self,obj):
        obj_packetName =  obj.hdl_conversion__.get_packet_file_name(obj)
        obj_entiyFileName =  obj.hdl_conversion__.get_entity_file_name(obj)
        i = 0 
        for x in gHDL_objectList:
            i +=1 
            packetName =  x.hdl_conversion__.get_packet_file_name(x)
            entiyFileName =  x.hdl_conversion__.get_entity_file_name(x)
            if obj_packetName ==  packetName and obj_entiyFileName == entiyFileName and type(obj) == type(x):
                #print(i)
                return x

        raise Exception("did not find primary object")

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
        ret =[]
        objName = str(obj)
        ret.append(name + " => " + objName)
        return  ret


    def _vhdl_get_attribute(self,obj, attName):
        return str(obj) + "." +str(attName)

    def _vhdl_slice(self,obj, sl,astParser=None):
        raise Exception("Not implemented")
        return obj
    
    def _vhdl__compare(self,obj, ops, rhs):
        return str(obj) + " " +ops2str(ops)+" " + str(rhs)

    def _vhdl__add(self,obj,args):
        return str(obj) + " + " + str(args)
    
    def _vhdl__Sub(self,obj,args):
        return str(obj) + " - " + str(args)

    def _vhdl__to_bool(self,obj, astParser):
        return "pyhdl_to_bool(" + str(obj) + ") "

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):
        obj._add_input()
        return obj

    def _vhdl__reasign_type(self, obj ):
        return obj

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        return str(obj) + " := " +  str(rhs)

    def get_get_call_member_function(self, obj, name, args):
        args = [x.get_symbol() for x in args ]

        needAdding =True
        for x  in obj.hdl_conversion__.MemfunctionCalls:
            if x["name"] != name:
                continue
            if not isSameArgs(args, x["args"] ,x['setDefault']):
                continue
            if x["call_func"] == None:
                needAdding = False
                continue
            return x
        if needAdding:
            obj.hdl_conversion__.MemfunctionCalls.append({
            "name" : name,
            "args": args,
            "self" :obj,
            "call_func" : None,
            "func_args" : None,
            "setDefault" : False

        })
        obj.IsConverted = False
        return None
    def _vhdl__call_member_func(self, obj, name, args, astParser=None):
        
        primary = obj.hdl_conversion__.get_primary_object(obj)
        if  primary is not obj:
            return primary.hdl_conversion__._vhdl__call_member_func( primary, name, args, astParser)
        
        
        call_obj = obj.hdl_conversion__.get_get_call_member_function(obj, name, args)

        if call_obj == None:
            primary.hdl_conversion__.MissingTemplate=True
            astParser.Missing_template = True
            print("Missing Template",name)
            return None
        print("use function of template ",name)
        call_func = call_obj["call_func"]
        if call_func:
            return call_func(obj, name, args, astParser, call_obj["func_args"])

        primary.hdl_conversion__.MissingTemplate=True
        astParser.Missing_template = True
        return None

        if name =="Connect":
            return str(obj)
        args_str = [ x.vhdl_name for x in args]
        args_str = [str(obj)] + args_str

        ret = join_str(args_str, Delimeter=", ", start= name+"(" ,end=")")
        return ret

    

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
        elif inOut == InOut_t.InOut_tt:
            return " inout "
        
        inOut = obj._writtenRead
        if inOut == InOut_t.input_t:
            return " in "
        elif inOut == InOut_t.output_t:
            return " out "
        elif inOut == InOut_t.InOut_tt:
            return " inout "
        raise Exception("unkown Inout type",inOut)

    def get_default_value(self,obj):
        return obj.type + "_null"


    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):
        if filter_inout and obj.Inout != filter_inout: 
            return []
        return [{ "suffix":"", "symbol": obj}]

    def get_Name_array(self,obj):
        return obj.hdl_conversion__.get_type_simple(obj)+"_a"

    def length(self,obj):
        return str(obj)+"'length"

class vhdl_base0:
    def __init__(self):
        super().__init__()
        if not isConverting2VHDL():
            gHDL_objectList.append(self)
        self._isInstance = False
        self.hdl_conversion__ = vhdl_converter_base()
        self.__Driver__ = None
        self.__receiver__ = []

    def _remove_connections(self):
        self.__Driver__ = None
        self.__receiver__ = []
        xs = self.getMember()
        for x in xs:
            x["symbol"]._remove_connections()

    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        return []

    def get_symbol(self):
        return self

    def DriverIsProcess(self):
        if type(self.__Driver__).__name__ == "str":
            return self.__Driver__ == "process"
        
        return False

        
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
    
    def _instantiate_(self):
        self._isInstance = True
        return self
    
    def _un_instantiate_(self):
        self._isInstance = False
        return self
    
    def _issubclass_(self,test):
        return "vhdl_base0" == test
    def _remove_drivers(self):
        self.__Driver__ = None

    def set_vhdl_name(self,name,Overwrite = False):
        raise Exception("update not implemented")                


class vhdl_base(vhdl_base0):

    def __init__(self):
        super().__init__()
        self.Inout         = InOut_t.Internal_t
        self._writtenRead  = InOut_t.Internal_t

    def _add_input(self):
        if self._writtenRead == InOut_t.Internal_t:
            self._writtenRead = InOut_t.input_t
        elif self._writtenRead == InOut_t.output_t:
            self._writtenRead = InOut_t.InOut_tt
        elif self._writtenRead == InOut_t.Used_t:
            self._writtenRead = InOut_t.input_t

    def _add_output(self):
        if self._writtenRead == InOut_t.Internal_t:
            self._writtenRead = InOut_t.output_t
        elif self._writtenRead == InOut_t.input_t:
            self._writtenRead = InOut_t.InOut_tt
        elif self._writtenRead == InOut_t.Used_t:
            self._writtenRead = InOut_t.output_t

    def _add_used(self):
        if self._writtenRead == InOut_t.Internal_t:
            self._writtenRead = InOut_t.Used_t
        elif self._writtenRead == InOut_t.Unset_t:
            self._writtenRead = InOut_t.Used_t

    def flipInout(self):
        pass
    def resetInout(self):
        pass
    def getName(self):
        return type(self).__name__

    def to_arglist(self,name,parent,withDefault = False):
        
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



    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "vhdl_base" == test





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

    if hasattr(Input,"get_value"):
        return Input.get_value()
    return Input

class  InOut_t(Enum):
    input_t    = 1
    output_t   = 2    
    Internal_t = 3
    Master_t   = 4
    Slave_t    = 5
    InOut_tt   = 6
    Default_t  = 7
    Unset_t    = 8 
    Used_t     = 9 

class varSig(Enum):
    variable_t = 1
    signal_t =2 
    const_t =3
    reference_t = 4
    combined_t = 5

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
    elif varSigConst == varSig.const_t:
        return  "constant"

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
    ret._remove_drivers()
    return ret
    
    
def v_signal(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret

def v_const(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.const_t)
    ret._remove_drivers()
    return ret

def port_out(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_out(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret

def port_in(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_in(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret

def port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret

def signal_port_Master(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret

def port_Stream_Master(symbol):
    ret = port_Master(symbol)
    ret._isInstance = False
    funcrec = inspect.stack()[1]
        
    f_locals = funcrec.frame.f_locals

    raise_if(f_locals["self"]._StreamOut != None, "the _StreamOut is already set")
 
    f_locals["self"]._StreamOut = ret
    ret._remove_drivers()                
    return ret 

def signal_port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret


def port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_Slave(symbol):
    ret= copy.deepcopy(symbol)
    ret._isInstance = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret

def port_Stream_Slave(symbol):
    ret = port_Slave(symbol)
    ret._isInstance = False
    funcrec = inspect.stack()[1]
        
    f_locals = funcrec.frame.f_locals
    raise_if(f_locals["self"]._StreamIn != None, "the _StreamIn is already set")
    
    f_locals["self"]._StreamIn = ret
    ret._remove_drivers()  
    return ret 
def v_copy(symbol,varSig=None):
    ret= copy.deepcopy(symbol)
    ret.resetInout()
    ret._isInstance = False
    ret.vhdl_name = None
    ret._remove_drivers()
    if varSig == None:
        ret.set_varSigConst(getDefaultVarSig())
    return ret



import ujson
def v_deepcopy(symbol):

    g =ujson.loads(ujson.dumps(symbol))
    return g