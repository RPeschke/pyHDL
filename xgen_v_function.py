import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
else:
    from .xgenBase import * 


class v_procedure_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()
    def getHeader(self, obj,name, parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = parent.hdl_conversion__.get_self_func_name (parent)

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
            classDef = parent.hdl_conversion__.get_self_func_name (parent)

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
        self.hdl_conversion__ = v_procedure_converter()
        self.argumentList = argumentList
        self.body = body
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction
    

    

class v_function_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()
    def getHeader(self, obj, name, parent):
        classDef =""
        if parent != None and not obj.isFreeFunction:
            classDef = parent.hdl_conversion__.get_self_func_name (parent,True)
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
            classDef = parent.hdl_conversion__.get_self_func_name(parent,True)
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
        self.hdl_conversion__ = v_function_converter()
        self.body = body
        self.returnType = returnType
        self.argumentList = argumentList
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction




class v_process_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()
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
    def __init__(self):
        super().__init__()

    def includes(self,obj, name,parent):
        inc_str = ""
        for x in obj.Symbols:
            inc_str +=  x.hdl_conversion__.includes(x, x.vhdl_name,obj)
        
        for x in obj.Arch_vars:
            inc_str +=  x['symbol'].hdl_conversion__.includes(x['symbol'], x['name'],obj)
        return inc_str

    def get_architecture_header(self, obj):
        header = ""
        for x in obj.Symbols:
            if x.type == "undef":
                continue
            header += x.hdl_conversion__.get_architecture_header(x)
        
        for x in obj.Arch_vars:
            header += x['symbol'].hdl_conversion__.get_architecture_header(x['symbol'])    
        return header


    def make_signal_list(self, obj, retList, objList):
        
        for x in objList:
            retList.append(x)
            obj.hdl_conversion__.make_signal_list(
                obj,
                retList, 
                x['symbol'].getMember(VaribleSignalFilter=varSig.signal_t)
            )

  
    def make_signal_connections(self, obj, objList):
        ret = ""
        for x in objList:
            if x['symbol'].__Driver__ and not x['symbol'].DriverIsProcess() and x['symbol'].__Driver__.vhdl_name:
                ret += x['symbol'].hdl_conversion__._vhdl__reasign(x['symbol'],x['symbol'].__Driver__)  +";\n  "
            else:
                ret += obj.hdl_conversion__.make_signal_connections(obj,x['symbol'].getMember(VaribleSignalFilter=varSig.signal_t))

        return ret
    def make_signal_connections2(self, obj, objList):
        ret = ""
        for x in objList:
            if x['symbol'].__Driver__ == None:
                continue
            if x['symbol'].DriverIsProcess():
                continue 
            if  x['symbol'].__Driver__.vhdl_name == None:
                continue 
            if  x['symbol'].varSigConst != varSig.signal_t:
                continue
            if  x['symbol'].__Driver__.varSigConst != varSig.signal_t:
                continue
            if not x['symbol'].vhdl_name:
                continue 
            if not list_is_in_list(x['symbol'].__Driver__, objList):
                continue
            ret += x['symbol'].hdl_conversion__._vhdl__reasign(x['symbol'],x['symbol'].__Driver__,context_str = "archetecture")  +";\n  "

        return ret
    def get_architecture_body(self, obj):
        body = ""  
        body += str(obj.body)
        for x in obj.Symbols:
            if x.type == "undef":
                continue
            line = x.hdl_conversion__.get_architecture_body(x) 
            if line.strip():
                body += "\n  " +line+";\n  "
        
        for x in obj.Arch_vars:
            line = x['symbol'].hdl_conversion__.get_architecture_body(x['symbol'])
            if line.strip():
                body += "\n  " + line  +";\n  "
        
        retList =[]
        obj.hdl_conversion__.make_signal_list(obj,retList,  obj.ports)
        obj.hdl_conversion__.make_signal_list(obj,retList,  obj.Arch_vars)
        retlist2 = list_make_unque(retList)
        body +=obj.hdl_conversion__.make_signal_connections2(obj, retlist2)
        #body +=obj.hdl_conversion__.make_signal_connections(obj, obj.Arch_vars)
 
        return body


    def getHeader(self, obj, name, parent):
        print("getHeader is dep")
        return ""

    def getBody(self,obj, name,parent):
        print("getHeader is dep")
        return ""

class v_Arch(vhdl_base):
    def __init__(self,body, Symbols,Arch_vars,ports):
        super().__init__()
        self.body = body 
        self.Symbols = Symbols
        self.Arch_vars = Arch_vars
        self.hdl_conversion__ = v_Arch_converter()
        self.ports = ports
        



def list_is_in_list(obj, ret):
    for y in ret:
        if obj is y["symbol"]:
            return True
    return False

def list_make_unque(objList):
    ret = []
    for x in objList:
        if not list_is_in_list(x["symbol"],ret):
            ret.append(x)

    return ret

