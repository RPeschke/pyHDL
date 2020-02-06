import ast

from .xgenBase import *
from .xgenAST import *
from .xgen_to_v_object import *



class v_package_converter(vhdl_converter_base):
    def includes(self, obj, name,parent):
        bufffer  = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            
            bufffer += t.vhdl_conversion__.includes(t,"",obj)
        sp = bufffer.split(";")
        sp  = [x.strip() for x in sp]
        sp = sorted(set(sp))
        ret = ""
        for x in sp:
            if len(x)>0:
                ret += x+";\n"
        return ret

    def getHeader(self, obj, name,parent):
        ret = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            ret += t.vhdl_conversion__.getHeader(t,"",obj)
        
        return ret

    def getBody(self,obj, name,parent):
        ret = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            ret += t.vhdl_conversion__.getBody(t,"",obj)
        
        return ret

class v_package(vhdl_base):
    def __init__(self, PackageName,PackageContent, sourceFile=None):
        super().__init__()
        self.vhdl_conversion__ = v_package_converter()
        
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        proc = isProcess()
        set_isProcess(True)
        self.PackageName = PackageName
        self.PackageContent = PackageContent
        self.astTree = None
        self.astv_classes = None
        if sourceFile:
            self.astTree = xgenAST(sourceFile)

            for x in self.PackageContent:
                if issubclass(type(x),v_class):
                    fun= list(self.astTree.extractFunctionsForClass(x ,self ))
                    for f in fun:
                        x.__ast_functions__.append(f)

        set_isConverting2VHDL(s)
        set_isProcess(proc)
            
    





   

    def getName(self):
        return type(self).__name__
    def to_string(self):
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        
        

        
        
        ret = "-- XGEN: Autogenerated File\n\n"
        ret += self.vhdl_conversion__.includes(self, None, self)
        ret += "\n\n"
        ret += "package " + self.PackageName + " is \n\n"
        ret += self.vhdl_conversion__.getHeader(self,None, self)
        ret += "end " + self.PackageName + ";\n\n\n"

        ret += "package body "+ self.PackageName +" is\n\n"
        ret += self.vhdl_conversion__.getBody(self,None, self)
        ret += "end "+ self.PackageName +";"

        set_isConverting2VHDL(s)
        return ret

    def getInstantByName(self,SymbolName):
        for t  in self.PackageContent:
            t = to_v_object(t)
            if t.name == SymbolName:
                return t


        raise Exception("unable to find type" , SymbolName)