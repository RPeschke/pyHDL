import  functools 

import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
    from CodeGen.xgen_v_symbol import *
else:
    from .xgenBase import *
    from .xgen_v_symbol import *



class v_entity_list_converter(vhdl_converter_base):
        def __init__(self):
            super().__init__()
        def get_architecture_header(self, obj):
            ret = "--------------------------"+ obj.vhdl_name  +"-----------------\n"
            VarSymb = "signal"
            i = 0
            for x in obj.nexted_entities:
                i+=1
                if x["temp"]:
                    tempName = obj.vhdl_name +"_"+ str(i) + "_" +type(x["symbol"]).__name__
                    x["symbol"].set_vhdl_name(tempName)
                    ret += x["symbol"].hdl_conversion__.get_architecture_header(x["symbol"])
            ret += "-------------------------- end "+ obj.vhdl_name  +"-----------------\n"
            return ret


        def get_architecture_body(self, obj):
            
            ret = ""
            i = 0
            start = ""
            for x in obj.nexted_entities:
                i+=1
                if x["temp"]:
                    tempName = str(obj.vhdl_name) +"_"+  str(i) + "_" +type(x["symbol"]).__name__
                    if not x["symbol"].vhdl_name:
                        x["symbol"].set_vhdl_name(tempName)
                    ret += start + x["symbol"].hdl_conversion__.get_architecture_body(x["symbol"])
                    start = ";\n  "
            


            return ret

        def includes(self,obj, name,parent):
            bufffer = ""
            
            for x in obj.nexted_entities:
                bufffer += x["symbol"].hdl_conversion__.includes(x["symbol"], None, None)

            ret  = make_unique_includes(bufffer)

            return ret

class v_entity_list(vhdl_base0):
    def __init__(self):
        super().__init__()
        self.hdl_conversion__ = v_entity_list_converter()
        self.nexted_entities = list()


        self.vhdl_name = ""
        self.type = "v_entity_list"
        self.astParser = None
    
    def __or__(self,rhs):

        

        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
        self.append(rhs)
        
        rhs_StreamIn << self_StreamOut
        
        return self
    
    def append(self, entity):
        if entity._issubclass_("v_symbol"):
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })
        elif entity._issubclass_("v_class"):
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })
        elif entity._isInstance == False:
            entity._instantiate_()
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : True
            })
        else:
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })


    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.nexted_entities:
            mem = x["symbol"].getMember(InOut_Filter, VaribleSignalFilter)
            ret += mem
        return ret

    def set_vhdl_name(self,name, Overwrite = False):
        if self.vhdl_name and self.vhdl_name != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name


    
    def set_simulation_param(self,module, name,writer):

        i = 0
        for x in self.nexted_entities:
            i+=1
            if x["temp"]:
                tempName =   name+"_"+str(i) + "_" +type(x["symbol"]).__name__
                x["symbol"].set_simulation_param(module, tempName,writer)

    


    def  __str__(self):
        ret = "----  --------- -------- " + self.vhdl_name +'----\n'
        return ret

    def _get_Stream_input(self):
        return self.nexted_entities[0]["symbol"]._get_Stream_output()


    def _get_Stream_output(self):
        return self.nexted_entities[-1]["symbol"]._get_Stream_output()


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_entity_list" == test