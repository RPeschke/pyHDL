from .xgenBase import * 


class v_list_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()

    def get_architecture_header(self, obj):


        ret =""
        if "std_logic_vector" in obj.Internal_Type.type:
            ret += """  type {objType} is array ({size} - 1 downto 0 ) of {Internal_Type};\n""".format(
                objType=obj.type,
                size = obj.get_size(),
                Internal_Type=obj.Internal_Type.type
            )
        if obj.varSigConst == varSig.variable_t:
            return ret
        VarSymb = get_varSig(obj.varSigConst)
        ret += """  {VarSymb} {objName} : {objType} := (others => {defaults});\n""".format(
            VarSymb=VarSymb,
            objName=obj.vhdl_name,
            objType=obj.type,
            defaults=obj.Internal_Type.DefaultValue
        )
        return ret

    def getHeader(self,obj, name,parent):
        return "v_list getHeader"    

    def _vhdl_slice(self,obj, sl,astParser=None):
        if issubclass(type(sl),vhdl_base0):
            sl = sl.hdl_conversion__._vhdl__getValue(sl,ReturnToObj="integer",astParser=astParser)
        
        ret = v_copy(obj.Internal_Type)
        ret.varSigConst = obj.varSigConst
        ret.vhdl_name =  obj.vhdl_name+"("+str(sl)+")"

        return ret
    def get_process_header(self,obj):
        if obj.varSigConst != varSig.variable_t:
            return ""
        ret =""
        VarSymb = get_varSig(obj.varSigConst)
        ret += """  {VarSymb} {objName} : {objType} := (others => {defaults});\n""".format(
            VarSymb=VarSymb,
            objName=obj.vhdl_name,
            objType=obj.type,
            defaults=obj.Internal_Type.DefaultValue
        )
        return ret
        
        
    def _vhdl__reasign(self, obj, rhs, context=None):
        asOp = obj.hdl_conversion__.get_assiment_op(obj)
        return str(obj.vhdl_name) + asOp +  str(rhs.vhdl_name)

class v_list(vhdl_base):
    def __init__(self,Internal_Type,size,varSigConst=None):
        super().__init__()
        self.hdl_conversion__ = v_list_converter()
        self.Internal_Type = Internal_Type
        self.content = []
        for i in range( value(size)):
            self.content.append( v_copy(Internal_Type) )

        self.size = size
        self.varSigConst = get_value_or_default(varSigConst, getDefaultVarSig())
        self.vhdl_name = None
        self.type = self.Internal_Type.hdl_conversion__.get_type_simple(self.Internal_Type)+"_a"

    def set_vhdl_name(self,name):
        if self.vhdl_name and self.vhdl_name != name:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name

    def get_size(self):
        return self.size

    def __getitem__(self,sl):
        return self.content[value(sl)]

    def set_simulation_param(self,module, name,writer):
        i = 0
        for x in self.content:
            x.set_simulation_param(module+"."+name, name+"(" +str(i)+")",writer)
            i+=1

    def setInout(self,Inout):
        self.Inout = Inout

    def set_varSigConst(self, varSigConst):
        self.varSigConst = varSigConst
        for x in self.content:
            x.set_varSigConst(varSigConst)

    def __lshift__(self, rhs):
        if len(self.content) != len(rhs.content):
            raise Exception("Differne list size")

        for x in range(len(self.content)):
            self.content[x] << rhs.content[x]