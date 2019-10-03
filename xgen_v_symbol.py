from .xgenBase import *
from .xgen_v_class import *



class v_symbol(vhdl_base):
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None):
        self.type = v_type
        self.DefaultValue = DefaultValue
        self.Inout = Inout
        self.inc = includes
        self.vhdl_name = None
        self.value = value


    def get_value(self):
        return self.value


    def isInOutType(self, Inout):
        if Inout == None:
            return True

        return self.Inout == Inout

    def getFuncArg(self,name,parent):
        return name + " : " + self.type   

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


    def recordMember(self,name, parent,Inout=None):
        
        #self.set_vhdl_name(name)

        if issubclass(type(parent),v_class):
            return "  " + name + " : " +self.type +"; \n"

        return ""

    def getType(self,Inout=None):
        return self.type

    def getTypes(self):
        return {
            "main" : self.type
        }

    def setInout(self,Inout):
        self.Inout = Inout
            
   
    
    def includes(self, name,parent):
        return self.inc
    
    
    def getHeader(self, name,parent):
        if self.vhdl_name:
            name = self.vhdl_name

        if issubclass(type(parent),v_class):
             return ""
            
        return name + " : " +self.type +" := " +  self.DefaultValue  + "; \n"
    
    def recordMemberDefault(self, name, parent,Inout=None):
        #if self.vhdl_name:
        #    name = self.vhdl_name
        
        if issubclass(type(parent),v_class):
            return name + " => " + self.DefaultValue 

        return ""

    def __str__(self):
        if self.vhdl_name:
            return self.vhdl_name

        return str(self.value)

    def _vhdl__reasign(self, rhs):
        if self.type == "std_logic":
            return str(self) + " := '" +  str(rhs) +"'"
        elif "std_logic_vector" in self.type:
            if str(rhs) == '0':
                return str(self) + " := (others => '0')"
            elif  issubclass(type(rhs),vhdl_base):
                return str(self) + " := " +  str(rhs) +""
            elif  type(rhs).__name__=="v_Num":
                return  """{dest} := std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=str(self),
                    src = str(rhs.value)
                )
        elif self.type == "integer":
            if str(rhs) == '0':
                return str(self) + " := 0"
            elif rhs.type == "integer":
                return str(self) + " := "+ str(rhs)
            elif "std_logic_vector" in rhs.type:
                return str(self) + " := to_integer(signed("+ str(rhs)+"))"

        return str(self) + " := " +  str(rhs)

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

    def _vhdl__DefineSymbol(self,VarSymb="variable"):
 
        name = self.vhdl_name

            
        return  VarSymb+ " " + name + " : " +self.type +" := " +  self.DefaultValue  + "; \n"

    def _vhdl_slice(self,sl):
        if "std_logic_vector" in self.type:
            ret = v_sl(self.Inout)
            ret.vhdl_name = self.vhdl_name+"("+str(sl)+")"
            return ret

        raise Exception("unexpected type")


   
def v_sl(Inout=InOut_t.Internal_t,Default="'0'"):
    return v_symbol(v_type= "std_logic", DefaultValue=Default, Inout = Inout,includes="""
library IEEE;
  use IEEE.std_logic_1164.all;
  use IEEE.numeric_std.all;

library UNISIM;
  use UNISIM.VComponents.all;
""")

def v_slv(BitWidth,Default="(others => '0')", Inout=InOut_t.Internal_t):
    value = Default
    if type(Default).__name__ == "int":
        Default =  'x"'+ hex(Default)[2:].zfill(int( int(BitWidth)/4))+'"'  

    return v_symbol(v_type="std_logic_vector(" + str(BitWidth -1) + " downto 0)",DefaultValue=Default,value=value,Inout=Inout,includes="""
library IEEE;
  use IEEE.std_logic_1164.all;
  use IEEE.numeric_std.all;
  use ieee.std_logic_unsigned.all;

library UNISIM;
  use UNISIM.VComponents.all;
""")

def v_int(Default="0",Inout=InOut_t.Internal_t):
    return v_symbol(v_type= "integer", DefaultValue=str(Default), Inout = Inout,includes="""
library IEEE;
  use IEEE.std_logic_1164.all;
  use IEEE.numeric_std.all;

library UNISIM;
  use UNISIM.VComponents.all;
""")

