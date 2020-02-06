from .xgenBase import *
from .xgen_v_class import *

from .xgen_simulation import *


class v_symbol_converter(vhdl_converter_base):
    def __init__(self,inc_str):
        self.inc_str  = inc_str

    def includes(self,obj, name,parent):
        return self.inc_str


    def recordMember(self,obj, name, parent,Inout=None):
        if issubclass(type(parent),v_class):
            return "  " + name + " : " +obj.type +"; \n"

        return ""

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        if issubclass(type(parent),v_class):
            return name + " => " + obj.DefaultValue 

        return ""

    def getHeader(self, obj,name,parent):
        if obj.vhdl_name:
            name = obj.vhdl_name

        if issubclass(type(parent),v_class):
             return ""
            
        return name + " : " +obj.type +" := " +  obj.DefaultValue  + "; \n"

    def getFuncArg(self,obj, name,parent):
        return name + " : " + obj.type   

class v_symbol(vhdl_base):
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t):
        super().__init__()
        if not varSigConst:
            varSigConst = getDefaultVarSig()

        self.vhdl_conversion__= v_symbol_converter(includes)
        self.type = v_type
        self.DefaultValue = str(DefaultValue)
        self.Inout = Inout
        self.inc = ""
        self.vhdl_name = None
        self.value = value
        self.nextValue  = value
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

        return self.Inout == Inout



    def to_arglist(self,name,parent):
        inoutstr = InOut_t2str(self.Inout)
        if not inoutstr:
            inoutstr = ""
        return name + " : " + inoutstr +" " + self.getType()

    def set_vhdl_name(self,name):
        if self.vhdl_name and self.vhdl_name != name:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name




    def getType(self,Inout=None):
        return self.type

    def getTypes(self):
        return {
            "main" : self.type
        }

    def setInout(self,Inout):
        self.Inout = Inout
            
    def set_varSigConst(self, varSigConst):
        self.varSigConst = varSigConst
        
    

    
    

    def get_type(self):
        return self.type



    def __str__(self):
        if self.__Driver__ != None and str( self.__Driver__) != 'process':
            ret =  str(self.__Driver__)
            if ret :
                return ret

        if self.vhdl_name:
            return self.vhdl_name

        return ""

    def set_simulation_param(self,module, name,writer):
        

        #print( "set_simulation_param", self.vhdl_name, name)
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




    def _vhdl__reasign(self, rhs, context=None):
        if issubclass(type(rhs),vhdl_base0)  and str( self.__Driver__) != 'process':
            self.__Driver__ = rhs
        
        if isProcess():
            self.__Driver__ = 'process'

        asOp = get_assiment_op(self.varSigConst)
        
        if self.type == "std_logic":
            if type(rhs).__name__=="v_symbol":
                return str(self) + asOp + str(rhs._vhdl__getValue(self.type)) 
            
            return str(self) + asOp+  str(rhs) 
        elif "std_logic_vector" in self.type:
            if str(rhs) == '0':
                return str(self) + asOp+ " (others => '0')"
            elif  issubclass(type(rhs),vhdl_base):
                return str(self) + asOp +  str(rhs._vhdl__getValue(self.type)) 
            elif  type(rhs).__name__=="v_Num":
                return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=str(self),
                    src = str(rhs.value),
                    asOp=asOp
                )
        elif self.type == "integer":
            if str(rhs) == '0':
                return str(self) + asOp+ " 0"
            elif type(rhs).__name__ == "str":
                return str(self) + asOp+ str(rhs)
                
            elif rhs.type == "integer":
                return str(self) + asOp+ str(rhs)
            elif "std_logic_vector" in rhs.type:
                return str(self) + asOp +" to_integer(signed("+ str(rhs)+"))"

        return str(self) +asOp +  str(rhs)

    def _vhdl__compare(self, ops, rhs):
        if self.type == "std_logic":
            value = str(rhs).lower()
            if value == "true":
                rhs = "1"
            elif value == "false":
                rhs = "0"            

            return str(self) + " "+ ops2str(ops)+" '" +  str(rhs) +"'"
        
        elif "std_logic_vector" in self.type:
            return str(self) + " "+ ops2str(ops)+" " +   str(rhs)
        

        return str(self) + " "+ ops2str(ops)+" " +   str(rhs)

    def _vhdl__make_constant(self, name):
        return "constant " + name + " : " +  self.type +" := " + str(self.DefaultValue) +";\n"


    def _vhdl__to_bool(self,astParser):
        if self.type == "std_logic":
            return str(self) + " = '1'"
        elif "std_logic_vector" in self.type:
            return str(self) + " > 1"
        elif self.type == "boolean":
            return str(self)
        elif self.type == "integer":
            return str(self) + " > 0"

        return "pyhdl_to_bool(" + str(self) + ") "

    def _vhdl__DefineSymbol(self,VarSymb=None):
        
        if not VarSymb:
            VarSymb = get_varSig(self.varSigConst)

        if  self.__Driver__ != None and str(self.__Driver__ ) != 'process':
            return ""
        name = self.vhdl_name

            
        return  VarSymb+ " " + name + " : " +self.type +" := " +  self.DefaultValue  + "; \n"

    def _vhdl_slice(self,sl):
        if "std_logic_vector" in self.type:
            ret = v_sl(self.Inout)
            ret.vhdl_name = self.vhdl_name+"("+str(sl)+")"
            return ret

        raise Exception("unexpected type")


slv_includes = """
library IEEE;
library UNISIM;
  use IEEE.numeric_std.all;
  use IEEE.std_logic_1164.all;
  use UNISIM.VComponents.all;
  use ieee.std_logic_unsigned.all;
  
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

def v_int(Default="0", Inout=InOut_t.Internal_t, varSigConst=None):
    return v_symbol(
        v_type= "integer", 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst
    )

