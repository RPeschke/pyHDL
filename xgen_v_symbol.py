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
            return name + " : " +obj.type

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


    def _vhdl__compare_int(self,obj, ops, rhs):
        return str(obj) + " "+ obj.hdl_conversion__.ops2str(ops) +" " +   str(rhs)

    def _vhdl__compare_std_logic(self,obj, ops, rhs):
        value = str(rhs).lower()
        if value == "true":
            rhs = "1"
        elif value == "false":
            rhs = "0"            
        return str(obj) + " "+ obj.hdl_conversion__.ops2str(ops) +" '" +  str(rhs) +"'"
    
    def _vhdl__compare_std_logic_vector(self,obj, ops, rhs):
        return str(obj) + " "+ obj.hdl_conversion__.ops2str(ops) +" " +   str(rhs)

    def _vhdl__compare(self,obj, ops, rhs):
        obj._add_input()
        if issubclass(type(rhs),vhdl_base):
            rhs._add_input()
    
        if obj.type == "integer":
            return obj.hdl_conversion__._vhdl__compare_int(obj, ops, rhs)
        elif obj.type == "std_logic":
            return obj.hdl_conversion__._vhdl__compare_std_logic(obj, ops, rhs)
        elif "std_logic_vector" in obj.type:
            return obj.hdl_conversion__._vhdl__compare_std_logic_vector(obj, ops, rhs)
        

        return str(obj) + " "+ obj.hdl_conversion__.ops2str(ops)+" " +   str(rhs)

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


    def _vhdl__reasign_std_logic(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.hdl_conversion__.get_assiment_op(obj)
        if issubclass(type(rhs),vhdl_base0):
            return target + asOp + str(rhs.hdl_conversion__._vhdl__getValue(rhs, obj.type)) 
        return target + asOp+  str(rhs) 

    def _vhdl__reasign_std_logic_vector(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.hdl_conversion__.get_assiment_op(obj)
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
    def _vhdl__reasign_int(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.hdl_conversion__.get_assiment_op(obj)
        if str(rhs) == '0':
            return target + asOp+ " 0"
        elif type(rhs).__name__ == "str":
            return target + asOp+ str(rhs)
                
        elif rhs.type == "integer":
            return target + asOp+ str(rhs)
        elif "std_logic_vector" in rhs.type:
            return target + asOp +" to_integer(signed("+ str(rhs)+"))"
        
        return target +asOp +  str(rhs)

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        obj._add_output()
        target = str(obj)
        if obj.varSigConst == varSig.signal_t and not (context_str and (context_str == "archetecture" or context_str== "process")):
            target = target.replace(".","_")

        if issubclass(type(rhs),vhdl_base0)  and str( obj.__Driver__) != 'process':
            obj.__Driver__ = rhs
        
        if isProcess():
            obj.__Driver__ = 'process'

        
        if obj.type == "std_logic":
            return obj.hdl_conversion__._vhdl__reasign_std_logic(obj, rhs,target, astParser,context_str)
        elif "std_logic_vector" in obj.type:
            return obj.hdl_conversion__._vhdl__reasign_std_logic(obj, rhs,target, astParser,context_str)
        elif obj.type == "integer":
            return obj.hdl_conversion__._vhdl__reasign_int(obj, rhs,target, astParser,context_str)

        asOp = obj.hdl_conversion__.get_assiment_op(obj)            
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

    def to_arglist(self,obj, name,parent,withDefault = False):
        inoutstr = obj.hdl_conversion__.InOut_t2str(obj)
        varSigstr = ""
        if obj.varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and obj._writtenRead != InOut_t.output_t and obj.Inout != InOut_t.output_t:
            default_str =  " := " + obj.hdl_conversion__.get_default_value(obj)

        return varSigstr + name + " : " + inoutstr +" " + obj.getType() + default_str

class v_symbol(vhdl_base):
    value_list = []
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
        self.value_list.append(get_value_or_default(value, DefaultValue))
        self.value_index = len(self.value_list) -1
        #self.value = get_value_or_default(value, DefaultValue)
        self.nextValue  = get_value_or_default(value, DefaultValue)
        self.varSigConst=varSigConst
        self.__Driver__ = None 
        self._update_list = list()
        self._update_list_process = list()
        self._update_list_running =[]
        self._update_list_process_running = list()
        self._receiver_list_running = []
        self._got_update_list = False
        self._Pull_update_list = list()
        self._Push_update_list = list()
        self.__vcd_varobj__ = None
        self.__vcd_writer__ = None
        self.__UpdateFlag__ = False
        self._Simulation_name = "NotSet"





    def _sim_get_value(self):
        return self.value_list[self.value_index]


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
        self._Simulation_name =module+"." +name
        self.__vcd_varobj__ = writer.register_var(module, name, 'integer', size=32)
        self.__vcd_writer__ = writer 
        self.vhdl_name = name
        self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())

    def _sim_write_value(self):
        if self.__vcd_writer__:
            self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())
        
        for x in self._receiver_list_running:
            x._sim_write_value()

    def update_init(self):# Only needs to run once on init
        if not self._got_update_list:
            self._update_list_process_running = list(set(self._sim__update_list_process()))
            self._update_list_running =     list(set(self._sim_get_update_list()))
            self._receiver_list_running  = self._sim_get_receiver()
            self._got_update_list = True


    def update(self):
        self.update_init() # Wrong Place here but it works 

        self.value_list[self.value_index]  = self.nextValue

        self._sim_write_value()
        
        gsimulation.append_updateList(self._update_list_running)
        gsimulation.append_updateList_process(self._update_list_process_running)

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

    def _sim_get_new_storage(self):
        self.value_list.append(value(self))
        self.value_index = len(self.value_list) -1  

    def _sim_get_update_list(self):
        ret = self._update_list
        for x in self.__receiver__:
            ret += x._sim_get_update_list()
        return ret
    def _sim_get_receiver(self):
        ret = self.__receiver__
        for x in self.__receiver__:
            ret += x.__receiver__
        return ret
    
    def _sim_get_primary_driver(self):
        ret = self
        if self.__Driver__:
            ret = self.__Driver__._sim_get_primary_driver()
        return ret

    def _sim_set_new_value_index(self,Index):
        self.value_index = Index
        receivers = self._sim_get_receiver()
        for x in receivers:
            x.value_index = self.value_index
    
    def _sim__update_list_process(self):
        ret = self._update_list_process
        for x in self.__receiver__:
            ret += x._sim__update_list_process()
        return ret

    def _sim_start_simulation(self):
        self._update_list_process_running = self._sim__update_list_process()
        self._update_list_running =self._sim_get_update_list()


    def _sim_append_update_list(self,up):
        self._update_list.append(up)
    


    def _instantiate_(self):
        self._isInstance = True
        self.Inout = InoutFlip(self.Inout)
        return self
        
    def _un_instantiate_(self, Name = ""):
        self._isInstance = False
        self.flipInout()
        self.set_vhdl_name(Name,True)
        return self

    def __bool__(self):
        return value(self) > 0


    def _Connect_running(self, rhs):
        self.nextValue = value(rhs)
        #print("assing: ", self.value_index , self._Simulation_name ,  value(rhs))

        if self.nextValue !=  value(self):
            def update():
                self.update()

            if not self.__UpdateFlag__:
                gsimulation.append_updateList([update])
                self.__UpdateFlag__ = True
                
        if self.varSigConst == varSig.variable_t:
            self.value_list[self.value_index]  = self.nextValue

    def _Conect_Not_running(self,rhs):
        if self.__Driver__ != None and not isConverting2VHDL():#todo: there is a bug with double assigment in the conversion to vhdl
            raise Exception("symbol has already a driver", str(self))
        elif not issubclass(type(rhs),vhdl_base0):
            self.nextValue = rhs
            self.value_list[self.value_index] = rhs
            return

        if rhs.varSigConst == varSig.variable_t or self.varSigConst == varSig.variable_t:
            self.value_list[self.value_index] = value(rhs)
            def update1():
                #print("update: ", self.value_index , self._Simulation_name ,  value(rhs))
                self.nextValue = value(rhs)
                self.update()
            rhs._update_list.append(update1)
        else:
            self.__Driver__ = rhs
            rhs.__receiver__.append(self)
            self.nextValue = rhs.nextValue
            self._sim_set_new_value_index(  rhs._sim_get_primary_driver().value_index )

        
        
    def __lshift__(self, rhs):
        if gsimulation.isRunning():
            self._Connect_running(rhs)
        else:
            self._Conect_Not_running(rhs)
            





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

