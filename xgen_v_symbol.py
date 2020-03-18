import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
    from CodeGen.xgen_simulation import *
else:
    from .xgenBase import *
    from .xgen_simulation import *


class v_symbol_converter(vhdl_converter_base):
    def __init__(self,inc_str):
        super().__init__()
        self.inc_str  = inc_str

    def includes(self,obj, name,parent):
        ret = slv_includes
        ret += self.inc_str
        return ret


    def recordMember(self,obj, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            return "  " + name + " : " +obj.type +"; \n"

        return ""

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        if parent._issubclass_("v_class"):
            return name + " => " + obj.DefaultValue 

        return ""

    def getHeader(self, obj,name,parent):
        if obj.vhdl_name:
            name = obj.vhdl_name

        if parent._issubclass_("v_class"):
             return ""
            
        return name + " : " +obj.type +" := " +  obj.DefaultValue  + "; \n"

    def getFuncArg(self,obj, name,parent):
        return name + " : " + obj.type   

    def _vhdl_slice(self,obj,sl,astParser=None):
        obj._add_input()
        if "std_logic_vector" in obj.type:
            ret = v_sl(obj.Inout)
            ret.vhdl_name = obj.vhdl_name+"("+str(sl)+")"
            return ret

        raise Exception("unexpected type")


    def _vhdl__compare(self,obj, ops, rhs):
        obj._add_input()
        if issubclass(type(rhs),vhdl_base):
            rhs._add_input()
        if obj.type == "std_logic":
            value = str(rhs).lower()
            if value == "true":
                rhs = "1"
            elif value == "false":
                rhs = "0"            

            return str(obj) + " "+ ops2str(ops)+" '" +  str(rhs) +"'"
        
        elif "std_logic_vector" in obj.type:
            return str(obj) + " "+ ops2str(ops)+" " +   str(rhs)
        

        return str(obj) + " "+ ops2str(ops)+" " +   str(rhs)

    def _vhdl__to_bool(self,obj, astParser):
        obj._add_input()
        if obj.type == "std_logic":
            return str(obj) + " = '1'"
        elif "std_logic_vector" in obj.type:
            return str(obj) + " > 1"
        elif obj.type == "boolean":
            return str(obj)
        elif obj.type == "integer":
            return str(obj) + " > 0"

        return "pyhdl_to_bool(" + str(obj) + ") "

    def _vhdl__DefineSymbol(self,obj, VarSymb=None):
        print("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj.varSigConst)

        if  obj.__Driver__ != None and str(obj.__Driver__ ) != 'process':
            return ""
        name = obj.vhdl_name

            
        return  VarSymb+ " " + name + " : " +obj.type +" := " +  obj.DefaultValue  + "; \n"
    def get_architecture_header(self, obj):

        if obj.Inout != InOut_t.Internal_t and obj._isInstance == False:
            return ""
        
        if obj.varSigConst == varSig.variable_t:
            return ""
        
        
        VarSymb = get_varSig(obj.varSigConst)

        #if  obj.__Driver__ != None and str(obj.__Driver__ ) != 'process':
        #    return ""
        name = obj.vhdl_name

        ret = "  " + VarSymb+ " " + name + " : " +obj.type +" := " +  obj.DefaultValue  + "; \n"   
        return  ret

    def get_port_list(self,obj):
        ret = []
        if obj.Inout == InOut_t.Internal_t:
            return ret
        
        if obj.varSigConst != varSig.signal_t:
            return ret
        
        ret.append( obj.vhdl_name + " : "+ obj.hdl_conversion__.InOut_t2str(obj) + " " + obj.type + " := " + obj.DefaultValue)
        return ret



    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        obj._add_output()
        target = str(obj)
        if obj.varSigConst == varSig.signal_t and not (context_str and (context_str == "archetecture" or context_str== "process")):
            target = target.replace(".","_")

        if issubclass(type(rhs),vhdl_base0)  and str( obj.__Driver__) != 'process':
            obj.__Driver__ = rhs
        
        if isProcess():
            obj.__Driver__ = 'process'

        asOp = obj.hdl_conversion__.get_assiment_op(obj)
        
        if obj.type == "std_logic":
            if issubclass(type(rhs),vhdl_base0):
                return target + asOp + str(rhs.hdl_conversion__._vhdl__getValue(rhs, obj.type)) 
            
            return target + asOp+  str(rhs) 
        elif "std_logic_vector" in obj.type:
            if str(rhs) == '0':
                return target + asOp+ " (others => '0')"
            elif  issubclass(type(rhs),vhdl_base):
                return target + asOp +  str(rhs.hdl_conversion__._vhdl__getValue(rhs, obj.type)) 
            elif  type(rhs).__name__=="v_Num":
                return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=target,
                    src = str(rhs.value),
                    asOp=asOp
                )
        elif obj.type == "integer":
            if str(rhs) == '0':
                return target + asOp+ " 0"
            elif type(rhs).__name__ == "str":
                return target + asOp+ str(rhs)
                
            elif rhs.type == "integer":
                return target + asOp+ str(rhs)
            elif "std_logic_vector" in rhs.type:
                return target + asOp +" to_integer(signed("+ str(rhs)+"))"

        return target +asOp +  str(rhs)
    
    def get_type_simple(self,obj):
        ret = obj.type
        if "std_logic_vector" in ret:
            sp1 = int(ret.split("downto")[0].split("(")[1])
            sp2 = int(ret.split("downto")[1].split(")")[0])
            sp3 = sp1 -sp2 +1
            ret  = "slv"+str(sp3)
        return ret

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):
        obj._add_input()
        if ReturnToObj == "integer" and  "std_logic_vector" in obj.type:
            return  "to_integer(signed( " + str(obj)  + "))"
        
        return obj

    def get_default_value(self,obj):
        return obj.DefaultValue

    def length(self,obj):
        ret = v_int()
        ret.vhdl_name=str(obj)+"'length"
        return ret


class v_symbol(vhdl_base):
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t):
        super().__init__()
        if not varSigConst:
            varSigConst = getDefaultVarSig()

        self.hdl_conversion__= v_symbol_converter(includes)
        self.type = v_type
        self.DefaultValue = str(DefaultValue)
        self.Inout = Inout
        
        self.inc = ""
        self.vhdl_name = None
        self.value = get_value_or_default(value, DefaultValue)
        self.nextValue  = get_value_or_default(value, DefaultValue)
        self.varSigConst=varSigConst
        self.__Driver__ = None 
        self._update_list = list()
        self._update_list_process = list()
        
        self._Pull_update_list = list()
        self._Push_update_list = list()
        self.__vcd_varobj__ = None
        self.__vcd_writer__ = None
        self.__UpdateFlag__ = False



    def length(self):
        return str(self)+"'length"

    def _sim_get_value(self):
        return self.value


    def isInOutType(self, Inout):
        if Inout == None:
            return True
        if self.Inout == InOut_t.InOut_tt:
            return True

        return self.Inout == Inout

    def isVarSigType(self, varSigType):
        if varSigType == None:
            return True

        return self.varSigConst == varSigType

    def to_arglist(self,name,parent,withDefault = False):
        inoutstr = self.hdl_conversion__.InOut_t2str(self)
        varSigstr = ""
        if self.varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and self._writtenRead != InOut_t.output_t and self.Inout != InOut_t.output_t:
            default_str =  " := " + self.hdl_conversion__.get_default_value(self)

        return varSigstr + name + " : " + inoutstr +" " + self.getType() + default_str

    def set_vhdl_name(self,name, Overwrite = False):
        if self.vhdl_name and self.vhdl_name != name and Overwrite==False:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name




    def getType(self,Inout=None):
        return self.type

    def getTypes(self):
        return {
            "main" : self.type
        }
    def resetInout(self):
        self.Inout = InOut_t.Internal_t
        
    def setInout(self,Inout):
        if self.Inout == InOut_t.Internal_t and  Inout == InOut_t.Master_t:
            self.Inout = InOut_t.output_t
            return 
        elif Inout == InOut_t.Master_t:
            return 

        elif self.Inout == InOut_t.Internal_t and  Inout == InOut_t.Slave_t:
            self.Inout = InOut_t.input_t
            return 
        elif Inout == InOut_t.Slave_t:
            self.Inout = InoutFlip(self.Inout)
            return 
        self.Inout = Inout


    def set_varSigConst(self, varSigConst):
        self.varSigConst = varSigConst
        
    
    def flipInout(self):
        self.Inout = InoutFlip(self.Inout)

    
    

    def get_type(self):
        return self.type



    def __str__(self):
        if self.vhdl_name:
            return str(self.vhdl_name)

        raise Exception("No Name was given to symbol")

    def set_simulation_param(self,module, name,writer):
        self.__vcd_varobj__ = writer.register_var(module, name, 'integer', size=32)
        self.__vcd_writer__ = writer 
        self.vhdl_name = name
        self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())

    def update(self):
        #print("update", self.vhdl_name)
        self.value = self.nextValue
        if self.__vcd_writer__:
            self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())
        
        for x in self._update_list:
            gsimulation.append_updateList(x)

        for x in self._update_list_process:
            gsimulation.append_updateList_process(x)
        #print("update",self.value)
        self.__UpdateFlag__ = False

##################### Operators #############################################
    def __add__(self,rhs):
        
        return value(self) + value(rhs) 

    def __sub__(self,rhs):
        
        return value(self) - value(rhs) 
        
    def __lt__(self,rhs):
        return value(self) < value(rhs) 

    def __gt__(self,rhs):
        return value(self) > value(rhs) 

    def __eq__(self,rhs):
        return value(self) == value(rhs) 
##################### End Operators #############################################
    def _sim_append_update_list(self,up):
        self._update_list.append(up)
    
    def _sim_append_Pull_update_list(self,up):
        self._Pull_update_list.append(up)

    def _sim_append_Push_update_list(self,up):
        self._Push_update_list.append(up)

    def _sim_run_pull(self):
        for x in self._Pull_update_list:
            x()

    def _sim_run_push(self):
            for x in self._Push_update_list:
                x()

    def _instantiate_(self):
        self._isInstance = True
        self.Inout = InoutFlip(self.Inout)
        return self
        
    # rhs is source
    def _connect(self,rhs):
        if self.Inout != rhs.Inout:
            raise Exception("Unable to connect different InOut types")
        if self.__Driver__ != None and not isConverting2VHDL():#todo: there is a bug with double assigment in the conversion to vhdl
            raise Exception("symbol has already a driver", str(self))
        #self.__Driver__ = rhs
        #print("_connect",self.vhdl_name)
        def update1():
            self.nextValue = rhs.value
            self.update()

        rhs._update_list.append(update1)

    def __bool__(self):
        
        return self.value > 0

    def __lshift__(self, rhs):
        if gsimulation.isRunning():
            
            if issubclass(type(rhs),vhdl_base0):
                self.nextValue = value(rhs)
            
            else:
                self.nextValue = rhs

            if self.nextValue != self.value:
                def update():
                    self.update()

                if not self.__UpdateFlag__:
                    gsimulation.append_updateList(update)
                    self.__UpdateFlag__ = True
                
            if self.varSigConst == varSig.variable_t:
                self.value = self.nextValue
                
            
        else:
            

            if self.__Driver__ != None and not isConverting2VHDL():#todo: there is a bug with double assigment in the conversion to vhdl
                raise Exception("symbol has already a driver", str(self))
            if issubclass(type(rhs),vhdl_base0):
                self.__Driver__ = rhs
                rhs.__receiver__.append(self)
                self.nextValue = rhs.nextValue
                self.value = rhs.value

                #print("__lshift__",self.vhdl_name)
                def update1():
                    self.nextValue = rhs.value
                    self.update()




                rhs._update_list.append(update1)
            else:
                self.nextValue = rhs
                self.value = rhs



    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_symbol" == test












slv_includes = """
library IEEE;
library UNISIM;
library work;
  use IEEE.numeric_std.all;
  use IEEE.std_logic_1164.all;
  use UNISIM.VComponents.all;
  use ieee.std_logic_unsigned.all;
  use work.hlpydlcore.all;
"""


def v_bool(Inout=InOut_t.Internal_t,Default=0,varSigConst=None):
    value = Default
    if type(Default).__name__ == "int":
        Default = "'" + str(Default) +"'"
    

    return v_symbol(
        v_type= "boolean", 
        DefaultValue=Default, 
        Inout = Inout,
        includes=slv_includes,
        value = value,
        varSigConst=varSigConst
    )
 
def v_sl(Inout=InOut_t.Internal_t,Default=0,varSigConst=None):
    value = Default
    if type(Default).__name__ == "int":
        Default = "'" + str(Default) +"'"
    

    return v_symbol(
        v_type= "std_logic", 
        DefaultValue=Default, 
        Inout = Inout,
        includes=slv_includes,
        value = value,
        varSigConst=varSigConst
    )

def v_slv(BitWidth=None,Default=0, Inout=InOut_t.Internal_t,varSigConst=None):


    value = Default
    if str(Default) == '0':
        Default = "(others => '0')"

    elif type(Default).__name__ == "int":
        Default =  'x"'+ hex(Default)[2:].zfill(int( int(BitWidth)/4))+'"'  
    
    v_type = ""
    if BitWidth == None:
        v_type="std_logic_vector"    
    elif type(BitWidth).__name__ == "int":
        v_type="std_logic_vector(" + str(BitWidth -1 ) + " downto 0)"
    else: 
        v_type = "std_logic_vector(" + str(BitWidth ) + " -1 downto 0)"

    return v_symbol(
        v_type=v_type, 
        DefaultValue=Default,
        value=value,
        Inout=Inout,
        includes=slv_includes,
        varSigConst=varSigConst
    )

def v_int(Default=0, Inout=InOut_t.Internal_t, varSigConst=None):
    
    return v_symbol(
        v_type= "integer",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst
    )

