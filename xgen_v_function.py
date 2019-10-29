from .xgenBase import * 



class v_procedure(vhdl_base):
    def __init__(self, argumentList="", body="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.argumentList = argumentList
        self.body = body
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction
    
    def getHeader(self, name, parent):
        classDef =""
        if parent and not self.isFreeFunction:
            classDef = " self : inout " + parent.getName()

        argumentList = optional_concatonat( classDef, "; ", self.argumentList)
        if self.name:
            name = self.name        
        if self.isEmpty:
            return "-- empty procedure removed. name: '"  + name +"'\n"

        ret = '''  procedure {functionName} ({argumentList});\n'''.format(
                functionName=name,
                argumentList=argumentList

        )
        return ret
    
    
    def getBody(self, name,parent):
        classDef =""
        if parent and not self.isFreeFunction:
            classDef = " self : inout " + parent.getName()

        argumentList = optional_concatonat( classDef, "; ", self.argumentList)
        if self.name:
            name = self.name      
        if self.isEmpty:
            return "-- empty procedure removed. name: '"  + name+"'\n"

        ret = '''procedure {functionName} ( {argumentList}) is\n  {VariableList} \n  begin \n {body} \nend procedure;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = self.body,
                VariableList=self.VariableList

        )
        return ret
    




class v_function(vhdl_base):
    def __init__(self,body="", returnType="", argumentList="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        self.body = body
        self.returnType = returnType
        self.argumentList = argumentList
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction


    def getHeader(self, name, parent):
        classDef =""
        if parent and not self.isFreeFunction:
            classDef = " self : " + parent.getName()
        argumentList = optional_concatonat( classDef, "; ", self.argumentList)
        if self.name:
            name = self.name
        if self.isEmpty:
            return "-- empty function removed. name: '"  + name+"'\n"

        ret = '''  function {functionName} (  {argumentList}) return {returnType};\n'''.format(
                functionName=name,
                argumentList=argumentList,
                returnType=self.returnType

        )
        return ret
    
    
    def getBody(self, name,parent):
        classDef =""
        if parent and not self.isFreeFunction:
            classDef = " self : " + parent.getName()
        argumentList = optional_concatonat( classDef, "; ", self.argumentList)
        
        if self.name:
            name = self.name  
        if self.isEmpty:
            return "-- empty function removed. name: '"  + name   +"'\n"

        ret = '''function {functionName} (  {argumentList}) return {returnType} is\n  {VariableList} \n  begin \n {body} \nend function;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = self.body,
                VariableList=self.VariableList,
                returnType=self.returnType

        )
        return ret





class v_process(vhdl_base):
    def __init__(self,body="", SensitivityList=None,VariableList="",prefix=None,name=None,IsEmpty=False):
        self.body = body 
        self.SensitivityList = SensitivityList
        self.VariableList = VariableList
        self.name = name
        self.IsEmpty = IsEmpty
        self.prefix = prefix


    def getBody(self, name,parent):
        ret = "process("+str(self.SensitivityList)+") is\n" +str(self.VariableList)+ "\n  begin\n"
        if self.prefix:
            ret += "  if " + str(self.prefix) + " then\n"
        ret += self.body
        if self.prefix:
            ret += "\n  end if;"
        ret += "\n end process;\n"
        return ret


class v_Arch(vhdl_base):
    def __init__(self,body="", Header="",prefix=None,name=None,IsEmpty=False):
        self.body = body 
        self.Header = Header
        self.name = name
        self.IsEmpty = IsEmpty
        self.prefix = prefix


    def getBody(self, name,parent):
        return self.body

    def getHeader(self, name, parent):
        return self.Header