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
    
