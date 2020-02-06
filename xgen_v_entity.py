from .xgenBase import *
from .xgen_v_symbol import *
from .axiStream import *
import  functools 



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
    return entity()

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
            onPushPull = f_locals[y]._sim_get_push_pull()
            if  onPushPull['_onPull']:
                symbol._sim_append_Pull_update_list( onPushPull['_onPull'])

            if onPushPull['_onPush']:
                symbol._sim_append_Push_update_list(onPushPull['_onPush'])
            
def addPullsPushes_from_closure(symbol,closure):
    for x in closure:
        y = x.cell_contents
        if issubclass(type(y), vhdl_base0):
            onPushPull = y._sim_get_push_pull()
            if  onPushPull['_onPull']:
                symbol._sim_append_Pull_update_list( onPushPull['_onPull'])

            if onPushPull['_onPush']:
                symbol._sim_append_Push_update_list(onPushPull['_onPush'])
            


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
            if issubclass(type(t),v_class):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
            elif issubclass(type(t),vhdl_base):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
        
        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret
class v_entiy2text:
    def __init__(self, input_entity):
        super().__init__()
        self.entity = input_entity
        self.astTree = None
        if input_entity._srcFileName:
            self.astTree = xgenAST(input_entity._srcFileName)
        
        self.getProcessBlocks()

    def get_Includes(self):
        bufffer = ""
        members= self.getMember()
        for x in members:
            bufffer += x.vhdl_conversion__.includes(x["symbol"],x["name"],None)

        for x in self.entity.__processList__:
            bufffer += x.vhdl_conversion__.includes(x,"",None)

        sp = bufffer.split(";")
        sp  = [x.strip() for x in sp]
        sp = sorted(set(sp))
        ret = ""
        for x in sp:
            if len(x)>0:
                ret += x+";\n"
        return ret
         
    
    def get_declaration(self):
        ret = "entity " + self.entity._name + " is \n" 
        members= self.getMember()
        start = "  "
        if len(members)>0:
            ret+="port(\n"
            for x in members:
                sym = x["symbol"]
                if sym.Inout == InOut_t.Internal_t:
                    continue
                elif sym.Inout == InOut_t.input_t or sym.Inout == InOut_t.output_t:
                    ret +=start+ x["name"] + " : "+ InOut_t2str(sym.Inout) + " " + sym.type + " := " + sym.DefaultValue 
                    start = ";\n  "
                elif sym.Inout == InOut_t.Slave_t:
                    types = sym.getTypes()
                    #ret += start+"-- " +x["name"]+" \n  "
                    ret += start+x["name"] + "_m2s : in  " +types["m2s"] + " := " + types["m2s"] + "_null"
                    start = ";\n  "   
                    ret +=start+ x["name"] + "_s2m : out " +types["s2m"] + " := " + types["s2m"] + "_null"
                    
                elif sym.Inout == InOut_t.Master_t:
                    types = sym.getTypes()
                    #ret += "-- <" +x["name"]+">\n  "
                    ret +=start+ x["name"] + "_m2s : out " +types["m2s"] + " := " + types["m2s"] + "_null"
                    start = ";\n  " 
                    ret +=start+ x["name"] + "_s2m : in  " +types["s2m"] + " := " + types["s2m"] + "_null"
                    #ret += "-- </" +x["name"]+">\n  "
        
            ret+="\n);\n"
        ret += "end entity;\n\n"
        return ret 

    def get_archhitecture_header(self):
        ret = ""
        members= self.getMember()
        
        for x in members:
            sym = x["symbol"]
            sym.set_vhdl_name(x["name"])
            if sym.Inout == InOut_t.Internal_t:
                ret += "  " + sym._vhdl__DefineSymbol("signal")
        
        for x in self.entity.__processList__:
            ret += x.vhdl_conversion__.getHeader(x,"",None)
        return ret 


    def get_archhitecture(self):

        ret = "architecture rtl of "+ self.entity._name +" is\n\n"
        ret += self.get_archhitecture_header()
        ret += "\nbegin\n"
        for x in self.entity.__processList__:
            ret += x.vhdl_conversion__.getBody(x,"",None)

        ret += "\nend architecture;\n"
        return ret 

    def get_definition(self):
        members= self.getMember()
        ret = ""

        ret += self.get_Includes()
        ret += "\n\n"
        ret += self.get_declaration()
        ret += "\n\n"
        ret += self.get_archhitecture()
        return ret

    def getProcessBlocks(self):
        ret = ""
        for x in self.entity.__dir__():
            if "_proc" in x:
                print(x)
        
        self.astTree.extractArchetectureForEntity(self.entity,None)


        return ret 


    def getMember(self):
        return v_entity_getMember(self.entity)

class v_entity_list(vhdl_base0):
    def __init__(self):
        self.nexted_entities = list()
        self._StreamOut = None
        self._StreamIn  = None
        self.vhdl_name = ""
        self.type = "v_entity_list"
        self.astParser = None
    
    def __or__(self,rhs):

        

        if self._StreamOut == None:
            raise Exception("output stream not defined")
        if rhs._StreamIn == None:
            raise Exception("Input stream not defined")
        
        rhs._StreamIn << self._StreamOut
        
        self.append(rhs)
        return self
    
    def append(self, entity):
        if entity._isInstance == False:
            entity()
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : True
            })
        else:
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })

        self._StreamOut = entity._StreamOut
        self._StreamIn = entity._StreamIn

    def set_vhdl_name(self, Name):
        self.vhdl_name  = Name

    def _vhdl__DefineSymbol(self,VarSymb=None):
        ret = ""
        if not VarSymb:
            VarSymb = get_varSig(self.varSigConst)
        i = 0
        for x in self.nexted_entities:
            i+=1
            if x["temp"]:
                tempName = self.vhdl_name +"_"+ str(i) + "_" +type(x["symbol"]).__name__
                x["symbol"].set_vhdl_name(tempName)
                ret += x["symbol"]._vhdl__DefineSymbol(VarSymb)


                    


        return ret
    
    def set_simulation_param(self,module, name,writer):

        i = 0
        for x in self.nexted_entities:
            i+=1
            if x["temp"]:
                tempName =   name+"_"+str(i) + "_" +type(x["symbol"]).__name__
                x["symbol"].set_simulation_param(module, tempName,writer)
            #print(x)
    
    def _vhdl__create(self, name):
        ret = ""
        i = 0
        start = ""
        for x in self.nexted_entities:
            i+=1
            if x["temp"]:
                tempName = self.vhdl_name +"_"+  str(i) + "_" +type(x["symbol"]).__name__
                ret += start + x["symbol"]._vhdl__create(tempName)
                start = ";\n  "
        
        for i in range(len(self.nexted_entities) -1):
            source = self.nexted_entities[i]
            destination = self.nexted_entities[i+1]
            rhs_StreamIn = destination["symbol"]._StreamIn
            lhs_StreamOut = source["symbol"]._StreamOut
            if issubclass( type(lhs_StreamOut),vhdl_base) and issubclass( type(rhs_StreamIn),vhdl_base):
                rhs_StreamIn = rhs_StreamIn._vhdl__reasign_type()
                lhs_StreamOut = lhs_StreamOut._vhdl__getValue(rhs_StreamIn,self.astParser)
                
                ret +=start+rhs_StreamIn._vhdl__reasign(lhs_StreamOut)
                start = ";\n  "

        return ret

    def  __str__(self):
        ret = ""
        start = ""
        for i in range(len(self.nexted_entities) -1):
            source = self.nexted_entities[i]
            destination = self.nexted_entities[i+1]
            rhs_StreamIn = destination["symbol"]._StreamIn
            lhs_StreamOut = source["symbol"]._StreamOut
            if issubclass( type(lhs_StreamOut),vhdl_base) and issubclass( type(rhs_StreamIn),vhdl_base):
                rhs_StreamIn = rhs_StreamIn._vhdl__reasign_type()
                lhs_StreamOut = lhs_StreamOut._vhdl__getValue(rhs_StreamIn,self.astParser)
                
                ret +=start+rhs_StreamIn._vhdl__reasign(lhs_StreamOut)
                start = ";\n  "

        return ret

                

class v_entity(vhdl_base0):
    def __init__(self,srcFileName=None):
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
        self._isInstance = False
        


    def __or__(self,rhs):

        

        if self._StreamOut == None:
            raise Exception("output stream not defined")
        if rhs._StreamIn == None:
            raise Exception("Input stream not defined")
        
        rhs_StreamIn = rhs._StreamIn
        self_StreamOut = self._StreamOut
        
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


    def architecture(self):
        pass

    def __call__(self):
        mem = v_entity_getMember(self)
        for x in mem:
            if not issubclass(type(self.__dict__[x["name"]]), vhdl_base):
                #del self.__dict__[x["name"]]
                continue

            if x["symbol"].Inout == InOut_t.Internal_t:
                #del self.__dict__[x["name"]]
                continue
            self.__dict__[x["name"]].Inout = InoutFlip( self.__dict__[x["name"]].Inout )
        
        self._isInstance = True
        return self

    def _get_definition(self):
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        
        to_text=v_entiy2text(self)

        ret = to_text.get_definition()
        set_isConverting2VHDL(s)
        return ret.strip()

    def _vhdl_get_adtribute(self,attName):
        if self.vhdl_name:
            return self.vhdl_name +"_"+ attName
        
        return attName

    def set_vhdl_name(self,name):
        self.vhdl_name = name   

    def _vhdl__DefineSymbol(self,VarSymb="variable"):
        ret =""
        mem = v_entity_getMember(self)
        for x in mem:
            if not x["symbol"].vhdl_name:
                x["symbol"].set_vhdl_name(self.vhdl_name +"_"+ x["name"])

            ret += x["symbol"]._vhdl__DefineSymbol(VarSymb)

        return ret 

    def _vhdl__create(self, name):
        ret = str(name) +" : entity work." + self._name+" port map ( \n"

        start = "    "
        mem = v_entity_getMember(self)
        for x in mem:
            if not x["symbol"].vhdl_name:
                x["symbol"].set_vhdl_name(self.vhdl_name+"_"+ x["name"])

            ret +=start + x["symbol"]._vhdl_make_port( x["name"] )
            start = ",\n    "

        ret += "\n)"
        return ret

class v_clk_entity(v_entity):
    def __init__(self,srcFileName=None,clk=None):
        super().__init__(srcFileName)
        self.clk    =  port_in(v_sl())
        if clk != None:
            self.clk <<  clk