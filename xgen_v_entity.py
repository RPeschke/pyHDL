from .xgenBase import *
from .xgen_v_symbol import *
from .axiStream import *

class v_entiy2text:
    def __init__(self, input_entity):
        self.entity = input_entity
        self.astTree = None
        if input_entity.srcFileName:
            self.astTree = xgenAST(input_entity.srcFileName)
        
        self.getProcessBlocks()

    def get_Includes(self):
        bufffer = ""
        members= self.getMember()
        for x in members:
            bufffer += x["symbol"].includes(x["name"],None)

        for x in self.entity.__processList__:
            bufffer += x.includes("",None)

        sp = bufffer.split(";")
        sp  = [x.strip() for x in sp]
        sp = sorted(set(sp))
        ret = ""
        for x in sp:
            if len(x)>0:
                ret += x+";\n"
        return ret
         
    
    def get_declaration(self):
        ret = "entity " + self.entity.name + " is \nport(\n" 
        members= self.getMember()
        start = "  "
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

        ret += "\n);\nend entity;\n\n"
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
            ret += x.getHeader("",None)
        return ret 


    def get_archhitecture(self):

        ret = "architecture rtl of "+ self.entity.name +" is\n\n"
        ret += self.get_archhitecture_header()
        ret += "\nbegin\n"
        for x in self.entity.__processList__:
            ret += x.getBody("",None)

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
        
        self.astTree.extractFunctionsForEntity(self.entity,None)


        return ret 
    def getMember(self):
        ret = list()
        for x in self.entity.__dict__.items():
            t = getattr(self.entity, x[0])
            if issubclass(type(t),vhdl_base):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })


        return ret
class v_entity:
    def __init__(self,name,srcFileName=None):
        self.name = name
        self.srcFileName = srcFileName
        self.__processList__ = list()
        self.Inout = ""

    def get_definition(self):
        to_text=v_entiy2text(self)

        return to_text.get_definition()

    def _vhdl_get_adtribute(self,attName):
        return attName

