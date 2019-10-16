from .xgenBase import *
from .xgen_v_class import *



class v_symbol(vhdl_base):
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t):
        self.type = v_type
        self.DefaultValue = DefaultValue
        self.Inout = Inout
        self.inc = includes
        self.vhdl_name = None
        self.value = value
        self.varSigConst=varSigConst

    def length(self):
        return str(self)+"'length"

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
    def get_type(self):
        return self.type

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
        if self.varSigConst== varSig.const_t:
            raise Exception("cannot asign to constant")
        elif self.varSigConst== varSig.signal_t:
            asOp = " <= "
        else: 
            asOp = " := "
        if self.type == "std_logic":
            if type(rhs).__name__=="v_symbol":
                return str(self) + asOp + rhs._vhdl__getValue(self.type) 
            
            return str(self) + asOp+"'" +  str(rhs) +"'"
        elif "std_logic_vector" in self.type:
            if str(rhs) == '0':
                return str(self) + asOp+ " (others => '0')"
            elif  issubclass(type(rhs),vhdl_base):
                return str(self) + asOp +  rhs._vhdl__getValue(self.type) 
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

    def _vhdl__DefineSymbol(self,VarSymb="variable"):
 
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
 
def v_sl(Inout=InOut_t.Internal_t,Default="'0'",varSigConst=varSig.variable_t):
    return v_symbol(v_type= "std_logic", DefaultValue=Default, Inout = Inout,includes=slv_includes,varSigConst=varSigConst)

def v_slv(BitWidth=None,Default="(others => '0')", Inout=InOut_t.Internal_t,varSigConst=varSig.variable_t):


    value = Default
    if type(Default).__name__ == "int":
        Default =  'x"'+ hex(Default)[2:].zfill(int( int(BitWidth)/4))+'"'  
    
    v_type = ""
    if BitWidth == None:
        v_type="std_logic_vector"    
    elif type(BitWidth).__name__ == "int":
        v_type="std_logic_vector(" + str(BitWidth -1 ) + " downto 0)"
    else: 
        v_type = "std_logic_vector(" + str(BitWidth ) + " -1 downto 0)"

    return v_symbol(v_type=v_type, DefaultValue=Default,value=value,Inout=Inout,includes=slv_includes,varSigConst=varSigConst)

def v_int(Default="0", Inout=InOut_t.Internal_t, varSigConst=varSig.variable_t):
    return v_symbol(v_type= "integer", DefaultValue=str(Default), Inout = Inout,includes=slv_includes,varSigConst=varSigConst)

