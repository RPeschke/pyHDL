from .xgenBase import * 


class v_procedure_converter(vhdl_converter_base):
    def getHeader(self, obj,name, parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = " self : inout " + parent.getName()

        argumentList = optional_concatonat( classDef, "; ", obj.argumentList)
        if obj.name:
            name = obj.name        
        if obj.isEmpty:
            return "-- empty procedure removed. name: '"  + name +"'\n"

        ret = '''  procedure {functionName} ({argumentList});\n'''.format(
                functionName=name,
                argumentList=argumentList

        )
        return ret
    
    
    def getBody(self, obj, name,parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = " self : inout " + parent.getName()

        argumentList = optional_concatonat( classDef, "; ", obj.argumentList)
        if obj.name:
            name = obj.name      
        if obj.isEmpty:
            return "-- empty procedure removed. name: '"  + name+"'\n"

        ret = '''procedure {functionName} ( {argumentList}) is\n  {VariableList} \n  begin \n {body} \nend procedure;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = obj.body,
                VariableList=obj.VariableList

        )
        return ret

class v_procedure(vhdl_base):
    def __init__(self, argumentList="", body="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.argumentList = argumentList
        self.body = body
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction
        self.hdl_conversion__ = v_procedure_converter()
    

    

class v_function_converter(vhdl_converter_base):

    def getHeader(self, obj, name, parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = " self : " + parent.getName()
        argumentList = optional_concatonat( classDef, "; ", obj.argumentList)
        if obj.name:
            name = obj.name
        if obj.isEmpty:
            return "-- empty function removed. name: '"  + name+"'\n"

        ret = '''  function {functionName} (  {argumentList}) return {returnType};\n'''.format(
                functionName=name,
                argumentList=argumentList,
                returnType=obj.returnType

        )
        return ret
    
    
    def getBody(self, obj, name,parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = " self : " + parent.getName()
        argumentList = optional_concatonat( classDef, "; ", obj.argumentList)
        
        if obj.name:
            name = obj.name  
        if obj.isEmpty:
            return "-- empty function removed. name: '"  + name   +"'\n"

        ret = '''function {functionName} (  {argumentList}) return {returnType} is\n  {VariableList} \n  begin \n {body} \nend function;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = obj.body,
                VariableList=obj.VariableList,
                returnType=obj.returnType

        )
        return ret

class v_function(vhdl_base):
    def __init__(self,body="", returnType="", argumentList="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.body = body
        self.returnType = returnType
        self.argumentList = argumentList
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction
        self.hdl_conversion__ = v_function_converter()




class v_process_converter(vhdl_converter_base):
    def getBody(self, obj,name,parent):
        ret = "process("+str(obj.SensitivityList)+") is\n" +str(obj.VariableList)+ "\n  begin\n"
        if obj.prefix:
            ret += "  if " + str(obj.prefix) + " then\n"
        ret += obj.body
        if obj.prefix:
            ret += "\n  end if;"
        ret += "\n end process;\n"
        return ret


class v_process(vhdl_base):
    def __init__(self,body="", SensitivityList=None,VariableList="",prefix=None,name=None,IsEmpty=False):
        super().__init__()
        self.body = body 
        self.SensitivityList = SensitivityList
        self.VariableList = VariableList
        self.name = name
        self.IsEmpty = IsEmpty
        self.prefix = prefix
        self.hdl_conversion__ = v_process_converter()





class v_Arch_converter(vhdl_converter_base):


    def includes(self,obj, name,parent):
        inc_str = ""
        for x in obj.Symbols:
            inc_str +=  x.hdl_conversion__.includes(x, x.vhdl_name,obj)
        return inc_str

    def get_architecture_header(self, obj):
        header = ""
        for x in obj.Symbols:
            if x.type == "undef":
                continue
            if  hasattr(x, 'varSigConst') and x.varSigConst == varSig.variable_t:
                continue
            header += x.hdl_conversion__.get_architecture_header(x)
            
        return header

    def get_architecture_body(self, obj):
        return  str(obj.body)


    def getHeader(self, obj, name, parent):
        print("getHeader is dep")
        return ""

    def getBody(self,obj, name,parent):
        print("getHeader is dep")
        return ""

class v_Arch(vhdl_base):
    def __init__(self,body, Symbols):
        super().__init__()
        self.body = body 
        self.Symbols = Symbols
        self.hdl_conversion__ = v_Arch_converter()
        




