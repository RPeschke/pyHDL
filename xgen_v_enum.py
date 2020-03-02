import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
else:
    from .xgenBase import * 



class v_enum(vhdl_base):
    def __init__(self,EnumIn,EnumVal=None,name=None):
        super().__init__()
        if type(EnumIn).__name__ == "EnumMeta":
            Enumtype = EnumIn
        elif type(type(EnumIn)).__name__ == "EnumMeta":
            Enumtype = type(EnumIn)
            EnumVal = EnumIn
            
        if EnumVal == None:
            EnumVal = Enumtype(0)

        if name == None:
            name = Enumtype.__name__

        self.type = Enumtype
        self.Value = EnumVal
        self.name = name
        self.Inout = InOut_t.Internal_t
        self.vhdl_name = None
    


        
    def set_vhdl_name(self,name, Overwrite = False):
        if self.vhdl_name and self.vhdl_name != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name

    def getHeader(self, name,parent):
        if  parent._issubclass_("v_class"):
             return ""
            
        # type T_STATE is (RESET, START, EXECUTE, FINISH);
        name = self.name
        enumNames =[e for e in self.type ] 
        start = "" 
        ret =  "\n  type " + name + " is ( \n    " 
        for x in enumNames:
            ret += start + x.name
            start = ",\n    "
        ret += "\n  );\n\n"
        return ret

    def recordMember(self,name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            if self.Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)
            return "  " + name + " : " +self.name +"; \n"
       
        return ""

    def recordMemberDefault(self, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            if self.Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)

            return name + " => " + self.Value.name 

        return ""
    

    def isInOutType(self, Inout):
        
        if Inout==None or self.Inout == Inout: 
            return True
        elif self.Inout== InOut_t.Master_t:
            mem = self.getMember(Inout)
            return len(mem) > 0
        elif self.Inout == InOut_t.Slave_t:
            if Inout == InOut_t.Master_t:
                Inout = InOut_t.Slave_t
            elif Inout == InOut_t.Slave_t:
                Inout = InOut_t.Master_t
            elif Inout == InOut_t.input_t:
                Inout = InOut_t.output_t
            elif Inout == InOut_t.output_t:
                Inout = InOut_t.input_t
            
            mem = self.getMember(Inout)
            return len(mem) > 0




    def __str__(self):
        if self.vhdl_name:
            return self.vhdl_name

        return str(self.Value.name)

    

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_enum" == test
        
