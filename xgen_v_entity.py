import  functools 

import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
    from CodeGen.xgen_v_symbol import *
    from CodeGen.xgen_v_entity_list import *
    from CodeGen.xgenAST import *
else:
    from .xgenBase import *
    from .xgen_v_symbol import *
    from .xgen_v_entity_list import *
    from .xgenAST import *


def end_architecture():
    add_symbols_to_entiy()

def process():
    def decorator_processd(func):
        @functools.wraps(func)
        def wrapper_process(getSymb=None):
            return func()
        localVarSig = getDefaultVarSig()

        setDefaultVarSig(varSig.variable_t)
        func()
        setDefaultVarSig(localVarSig)
        add_symbols_to_entiy()

        return wrapper_process
    return decorator_processd



def timed():
    def decorator_timed(func):
        @functools.wraps(func)
        def wrapper_timed(getSymb=None):
            return func()

        gsimulation.timmed_process.append(func)
        return wrapper_timed
    return decorator_timed

def v_create(entity):
    return entity._instantiate_()

class wait_for():
    def __init__(self,time,unit="ns"):
        self.time =time 
        self.unit = unit

    def get_time(self):
        return self.time

    def __str__(self):
        return " " + str(self.time) +" " + self.unit


def addPullsPushes(symbol):
    funcrec = inspect.stack()[2]
    funcrec4 = inspect.stack()[4]
    
        
    f_locals = funcrec.frame.f_locals
    f_locals4  = funcrec4.frame.f_locals
    for y in f_locals:
        if not y in f_locals4 and y != "self" and issubclass(type(f_locals[y]), vhdl_base0):
            f_locals[y]._sim_set_push_pull(symbol)

            
def addPullsPushes_from_closure(symbol,closure):
    if closure == None:
        return
    for x in closure:
        y = x.cell_contents
        if issubclass(type(y), vhdl_base0):
            y._sim_set_push_pull(symbol)
            



def combinational():
    def decorator_combinational(func):
        @functools.wraps(func)
        def wrapper_combinational():
            return func()

        for symb in func.__closure__:
            symbol = symb.cell_contents
            symbol._sim_append_update_list(wrapper_combinational)
        return wrapper_combinational
    return decorator_combinational

def v_switch(default_value, v_cases):
    for c in v_cases:
        if c["pred"]:
            return c["value"]

    return default_value

def v_case(pred,value):
    ret = {
        "pred" : pred,
        "value" : value 
    }
    return ret

def rising_edge(symbol):
    def decorator_rising_edge(func):
        @functools.wraps(func)
        def wrapper_rising_edge(getSymb=None):
            if symbol.value == 1:
                symbol._sim_run_pull()
                func()
                symbol._sim_run_push()
        symbol._update_list_process.append(wrapper_rising_edge)
        addPullsPushes_from_closure(symbol,func.__closure__)
        return wrapper_rising_edge
    return decorator_rising_edge

gport_veto__ =[
            "_StreamOut",
            "_StreamIn"
        ]

def v_entity_getMember(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x[0] in gport_veto__:
                continue

            t = getattr(entity, x[0])
            if issubclass(type(t),vhdl_base):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

def v_entity_getMember_expand(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x in gport_veto__:
                continue
            t = getattr(entity, x[0])
            if t._issubclass_("v_class"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
            elif t._issubclass_("vhdl_base"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
        
        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

        


class v_entity_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()
    def get_entity_file_name(self, obj):
        return type(obj).__name__+".vhd"

    def get_enity_file_content(self, obj):
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        
        obj._un_instantiate_()
        obj.hdl_conversion__.MissingTemplate = False
        
        obj.hdl_conversion__.parse_file(obj)
        
        ret = "-- XGEN: Autogenerated File\n\n"
        ret += obj.hdl_conversion__.includes(obj, None, obj)
        ret += "\n\n"
        
        ret += obj.hdl_conversion__.get_entity_definition(obj)
        
        obj._instantiate_()
        set_isConverting2VHDL(s)
        return ret

    def __init__(self):
        super().__init__()
        self.astTree = None


    def parse_file(self,obj):
        if obj._srcFileName:
            self.astTree = xgenAST(obj._srcFileName)
            self.astTree.extractArchetectureForEntity(obj,None)

        
    def _vhdl_get_attribute(self,obj, attName):
        if obj.vhdl_name:
            return obj.vhdl_name +"_"+ attName
        
        return attName

    def get_archhitecture(self,obj):

        ret = "architecture rtl of "+ obj._name +" is\n\n"

        ret +=  obj.hdl_conversion__.get_architecture_header_def(obj)
        ret += "\nbegin\n"
        ret +=  obj.hdl_conversion__.get_architecture_body_def(obj)
        ret += "\nend architecture;\n"
        return ret 

    def get_architecture_header_def(self, obj):
        if obj.vhdl_name:
            name = obj.vhdl_name
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.hdl_conversion__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            symName = obj.hdl_conversion__._vhdl_get_attribute(obj,x["name"])
            sym.vhdl_name = symName
            
            ret +=  sym.hdl_conversion__.get_architecture_header(sym)


        for x in obj.__processList__:
            ret += x.hdl_conversion__.get_architecture_header(x)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def get_architecture_header(self, obj):
        if obj.vhdl_name:
            name = obj.vhdl_name
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.hdl_conversion__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            if sym.Inout ==InOut_t.Internal_t:
                continue
            symName = obj.hdl_conversion__._vhdl_get_attribute(obj,x["name"])
            sym.vhdl_name = symName
            
            ret +=  sym.hdl_conversion__.get_architecture_header(sym)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def get_architecture_body(self, obj):

        content = []
        

        for x in v_entity_getMember(obj):
            if x["symbol"].Inout ==InOut_t.Internal_t:
                continue
            if not x["symbol"].vhdl_name:
                x["symbol"].set_vhdl_name(obj.vhdl_name+"_"+ x["name"])

            content += x["symbol"].hdl_conversion__._vhdl_make_port(x["symbol"], x["name"] )


        
        start = str(obj.vhdl_name) +" : entity work." + obj._name+" port map (\n    "
        ret=join_str(content,start=start ,end="\n  )",Delimeter=",\n    ")
      
  
        return ret
 

    def get_architecture_body_def(self, obj):
        ret = ""
        for x in obj.__processList__:
            ret += x.hdl_conversion__.get_architecture_body(x)
        return ret 



    def getMember(self, obj):
        return v_entity_getMember(obj)
    
    def includes(self,obj, name,parent):
        bufffer = ""
        members= obj.hdl_conversion__.getMember(obj)
        for x in members:
            bufffer += x["symbol"].hdl_conversion__.includes(x["symbol"],x["name"],None)

        for x in obj.__processList__:
            bufffer += x.hdl_conversion__.includes(x,"",None)


        ret = make_unique_includes(bufffer)
        return ret

    def get_declaration(self,obj):
        portdef=[]
        
        for x in obj.hdl_conversion__.getMember(obj):
            sym = x["symbol"]
            sym.vhdl_name = x["name"]
            portdef += sym.hdl_conversion__.get_port_list(sym)

      
        ret = "entity " + obj._name + " is \n" 
        ret+=join_str(portdef,start="  port(\n    " ,end="\n  );\n",Delimeter=";\n    ",IgnoreIfEmpty=True)
        ret += "end entity;\n\n"
        return ret

    def get_definition(self, obj):
    
        if obj._isInstance==True:
            obj._un_instantiate_()
        ret = ""

        #ret += obj.hdl_conversion__.includes(obj,None,None)
        ret += "\n\n"
        ret += obj.hdl_conversion__.get_declaration(obj)
        ret += "\n\n"
        ret += obj.hdl_conversion__.get_archhitecture(obj)
        return ret

    def get_entity_definition(self, obj):
        #s = isConverting2VHDL()
        #set_isConverting2VHDL(True)
        
        #obj.hdl_conversion__.parse_file(obj)

        ret = obj.hdl_conversion__.get_definition(obj)
        #set_isConverting2VHDL(s)
        return ret.strip()

class v_entity(vhdl_base0):
    def __init__(self,srcFileName=None):
        super().__init__()

        self.hdl_conversion__= v_entity_converter()
        setDefaultVarSig(varSig.signal_t)
        name = type(self).__name__
        self._name = name
        self._srcFileName = srcFileName
        self.__processList__ = list()
        self.Inout = ""
        self.vhdl_name = None
        self.type = "entity"
        self.__local_symbols__ = list()
        self._StreamOut = None
        self._StreamIn  = None

        
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if not issubclass(type(t),vhdl_base) :
                continue 
            if not t.isInOutType(InOut_Filter):
                continue
            
            if not t.isVarSigType(VaribleSignalFilter):
                continue

            ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret


    def __or__(self,rhs):

        
        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
                
        ret = v_entity_list()


        ret.append(self)
        ret.append(rhs)

        rhs_StreamIn << self_StreamOut
        return ret
        
    def set_simulation_param(self,module, name,writer):
        mem = v_entity_getMember(self)
        for x in mem:
            
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)
            #print(x)
        local_symbols =sorted(self.__local_symbols__, key=lambda element_: element_["name"])
        for x in local_symbols:
            
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)
            #print (x)


    def _add_symbol(self, name,symb):
        for x in self.__local_symbols__:
            if symb is x["symbol"]:
                return

        self.__local_symbols__.append(
            {
                "name" : name,
                "symbol" : symb
            }
        )


    def _instantiate_(self):
        if self._isInstance == True:
            return self
            
        mem = v_entity_getMember(self)
        for x in mem:
            if not issubclass(type(self.__dict__[x["name"]]), vhdl_base):
                #del self.__dict__[x["name"]]
                continue
            self.__dict__[x["name"]]._instantiate_()
        
        self._isInstance = True
        return self

    def _un_instantiate_(self):
        if self._isInstance == False:
            return self
        
        self.set_vhdl_name("", True)
        mem = v_entity_getMember(self)
        for x in mem:
            if not issubclass(type(self.__dict__[x["name"]]), vhdl_base):
                #del self.__dict__[x["name"]]
                continue
            self.__dict__[x["name"]]._isInstance = False
            self.__dict__[x["name"]].flipInout()
            self.__dict__[x["name"]].set_vhdl_name(x["name"],True)
        
        self._isInstance = False
        return self





    def set_vhdl_name(self,name, Overwrite = False):
        if self.vhdl_name and self.vhdl_name != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name

    def _sim_append_update_list(self,up):
        for x in self.getMember():
            x["symbol"]._sim_append_update_list(up)
    

    def _get_Stream_input(self):
        if self._StreamIn == None:
            raise Exception("Input stream not defined")
        return  self._StreamIn

    def _get_Stream_output(self):
        if self._StreamOut == None:
            raise Exception("output stream not defined")
        return self._StreamOut


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_entity" == test
        
class v_clk_entity(v_entity):
    def __init__(self,srcFileName=None,clk=None):
        super().__init__(srcFileName)
        self.clk    =  port_in(v_sl())
        if clk != None:
            self.clk <<  clk

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_clk_entity" == test