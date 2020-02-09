from .xgenBase import * 
from .xgen_v_function import *


class v_class_converter(vhdl_converter_base):


    def includes(self,obj, name,parent):
        ret = ""
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base):
                        
                ret += t.hdl_conversion__.includes(t,x[0],obj)
        
        for x in obj.__ast_functions__:
            ret += x.hdl_conversion__.includes(x,None,obj)
        return ret

    def recordMember(self,obj, name,parent,Inout=None):
        if issubclass(type(parent),v_class):
            if obj.Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)


            return "  " + name + " : " +obj.getType(Inout) +"; \n"

        
        return ""

    def recordMemberDefault(self, obj, name,parent,Inout=None):
        if issubclass(type(parent),v_class):
            if obj.Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)

            return name + " => " + obj.getType(Inout) + "_null"

        return ""

    def make_constant(self, obj, name,parent=None,InOut_Filter=None):
        TypeName = obj.getType(InOut_Filter)
        member = obj.getMember(InOut_Filter)
        ret = "\nconstant " + name + " : " + TypeName + ":= (\n  "
        start = ""
        for x in member:
            default = x["symbol"].hdl_conversion__.recordMemberDefault(x["symbol"], x["name"],obj,InOut_Filter)
            if default:
                ret += start + default
                start = ",\n  "
                
        ret += "\n);\n"
        return ret

    def getHeader(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        ret = "-------------------------------------------------------------------------\n"
        ret += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        if obj.__v_classType__ == v_classType_t.transition_t:     
            ret +=  obj.hdl_conversion__.getHeader_make_record(obj, name,parent,InOut_t.output_t)
            ret += "\n\n"
            ret +=  obj.hdl_conversion__.getHeader_make_record(obj, name,parent,InOut_t.input_t)
            ret += "\n\n"
        
        ret +=  obj.hdl_conversion__.getHeader_make_record(obj, name,parent)
        
        obj.hdl_conversion__.make_connection(obj,name,parent)
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base) and not issubclass(type(t),v_class):
                ret += t.hdl_conversion__.getHeader(t,x[0],obj)

        for x in obj.__ast_functions__:
            if x.name.lower() == "_onpull" or x.name.lower() == "_onpush":
                continue
            ret +=  x.hdl_conversion__.getHeader(x,None,None)


        ret += "------- End Psuedo Class " +obj.getName() +" -------------------------\n"
        ret += "-------------------------------------------------------------------------\n\n\n"
        return ret


    def getHeader_make_record(self,obj, name, parent=None, InOut_Filter=None):
        TypeName = obj.getType(InOut_Filter)
        member = obj.getMember(InOut_Filter)
        
        if len(member) == 0:
            return ""

        ret = "\ntype "+TypeName+" is record \n"
        for x in member:
            ret += x["symbol"].hdl_conversion__.recordMember(x["symbol"],x["name"],obj,InOut_Filter)
        ret += "end record;\n\n"



        ret += obj.hdl_conversion__.make_constant(obj,TypeName+ "_null", parent, InOut_Filter)
   
        ret += "\n\n"
        ret += "type "+ TypeName+"_a is array (natural range <>) of "+TypeName+";\n\n"
        return ret

    def make_connection(self, obj, name, parent):
            
        
        if obj.__v_classType__ == v_classType_t.transition_t:    
            obj.pull          =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "pull", "dataIn",procedureName="pull" )
            obj.pull_nc       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "pull",procedureName="pull")


            obj.push          =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "push", "dataOut",procedureName="push")
            obj.push_nc       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "push" ,procedureName="push")

            obj.pull_rev      =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "pull", "dataIn", procedureName="pull_rev")
            obj.pull_rev_nc   =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "pull" , procedureName="pull_rev")

            obj.push_rev      =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "push", "dataOut" ,procedureName="push_rev")
            obj.push_rev_nc   =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "push",procedureName="push_rev")

        elif obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
   
            obj.pull       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "pull")
            obj.push       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "push")

            if obj.__vectorPull__:
                obj.vpull       =  obj.hdl_conversion__.getConnecting_procedure_vector(obj, InOut_t.input_t , "pull",procedureName="pull")
            if obj.__vectorPush__:
                obj.vpush       =  obj.hdl_conversion__.getConnecting_procedure_vector(obj, InOut_t.output_t, "push",procedureName="push")

    def getConnecting_procedure_vector(self,obj, InOut_Filter,PushPull,procedureName=None):
        
        isEmpty = False
        if PushPull== "push":
            inout = " out "
            isEmpty = obj.push.isEmpty

        else:
            inout = " in "
            isEmpty = obj.pull.isEmpty

        TypeName = obj.getType(obj.__v_classType__)
        members = obj.getMember(InOut_Filter) 
        selfarg = "self : inout "+ TypeName+"_a"
        argumentList =  obj.hdl_conversion__.getMemberArgs(obj, InOut_Filter,inout,suffix="_a").strip()
        if argumentList:
            selfarg += "; " +argumentList
        args =""
        start =", "
        for x in members:
            args+= start + x["name"]+"(i)"
            
        ret        = v_procedure(name=procedureName, argumentList=selfarg , body='''
        for i in 0 to self'length - 1 loop
        {PushPull}(self(i) {args});
        end loop;
            '''.format(
                PushPull=PushPull,
                args = args
            ),
            isFreeFunction=True,
            IsEmpty=isEmpty
            )

        return ret

    def getConnecting_procedure(self,obj, InOut_Filter,PushPull,ClassName=None,procedureName=None):
        if PushPull== "push":
            beforeConnecting = obj.__BeforePush__
            beforeConnecting += obj.getBody_onPush()
            AfterConnecting = obj.__AfterPush__
            inout = " out "
            
            if InOut_Filter == InOut_t.input_t:
                classType = obj.__NameSlave2Master__
            elif InOut_Filter == InOut_t.output_t:
                classType = obj.__NameMaster2Slave__     
            else:
                raise Exception("unexpected combination")

        else:
            beforeConnecting = obj.__BeforePull__
            AfterConnecting = obj.__AfterPull__
            AfterConnecting += obj.getBody_onPull()
            inout = " in "

            if InOut_Filter == InOut_t.input_t:
                classType = obj.__NameSlave2Master__  
            elif InOut_Filter == InOut_t.output_t:
                classType = obj.__NameMaster2Slave__    
            else:
                raise Exception("unexpected combination")

        if  ClassName:
            argumentList = "signal " + ClassName +" : " + inout+ classType
        else:
            argumentList = obj.hdl_conversion__.getMemberArgs(obj, InOut_Filter,inout)

        Connecting = obj.hdl_conversion__.getMemeber_Connect(obj, InOut_Filter,PushPull, ClassName)
        IsEmpty=len(Connecting.strip()) == 0 and len(beforeConnecting.strip()) == 0 and  len(AfterConnecting.strip()) == 0
        ret        = v_procedure(name=procedureName, argumentList=argumentList , body='''
    {beforeConnecting}
-- Start Connecting
    {Connecting}
-- End Connecting
    {AfterConnecting}
            '''.format(
               beforeConnecting=beforeConnecting,
               Connecting = Connecting,
               AfterConnecting=AfterConnecting
            ),
            IsEmpty=IsEmpty
            )
        
        return ret

    def getBody(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        ret = "-------------------------------------------------------------------------\n"
        ret += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base):
                ret += t.hdl_conversion__.getBody(t,x[0],obj)
        
        for x in obj.__ast_functions__:
            if x.name.lower() == "_onpull" or x.name.lower() == "_onpush":
                continue
            ret +=  x.hdl_conversion__.getBody(x,None,None)

        ret += "------- End Psuedo Class " +obj.getName() +" -------------------------\n  "
        ret += "-------------------------------------------------------------------------\n\n\n"
        return ret
    
    def _vhdl__DefineSymbol(self, obj ,VarSymb=None):
        print("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj.varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret = ""
            ret += VarSymb + " " +str(obj) + "_m2s : " + t["m2s"] +" := " + t["m2s"]+"_null;\n"
            ret += VarSymb + " " +str(obj) + "_s2m : " + t["s2m"] +" := " + t["s2m"]+"_null;\n"
            return ret

        return VarSymb +" " +str(obj) + " : " +obj.type +" := " + obj.type+"_null;\n"
    

    def get_architecture_header(self, obj):
        if obj.Inout != InOut_t.Internal_t and obj._isInstance == False:
            return ""
        
        if obj.varSigConst != varSig.signal_t or obj.varSigConst != varSig.signal_t:
            return ""

        VarSymb = get_varSig(obj.varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret = ""
            ret += "  " + VarSymb + " " +str(obj) + "_m2s : " + t["m2s"] +" := " + t["m2s"]+"_null;\n"
            ret += "  " + VarSymb + " " +str(obj) + "_s2m : " + t["s2m"] +" := " + t["s2m"]+"_null;\n"
            return ret

        return "  " + VarSymb +" " +str(obj) + " : " +obj.type +" := " + obj.type+"_null;\n"
        
    def get_port_list(self,obj):
        ret = ""
        if obj.Inout == InOut_t.Internal_t:
            return ""
        
        if obj.varSigConst != varSig.signal_t:
            return ""
        
        if obj.Inout == InOut_t.Slave_t:
            types = obj.getTypes()
            ret += obj.vhdl_name + "_m2s : in  " +types["m2s"] + " := " + types["m2s"] + "_null;\n  "
            ret += obj.vhdl_name + "_s2m : out " +types["s2m"] + " := " + types["s2m"] + "_null"
                    
        elif obj.Inout == InOut_t.Master_t:
            types = obj.getTypes()
            ret += obj.vhdl_name + "_m2s : out " +types["m2s"] + " := " + types["m2s"] + "_null;\n  "
            ret += obj.vhdl_name + "_s2m : in  " +types["s2m"] + " := " + types["s2m"] + "_null"
            
        return ret


    def _vhdl_make_port(self, obj, name):
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret = ""
            ret += name + "_m2s => " + str(obj)+"_m2s, \n    "
            ret += name + "_s2m => " + str(obj)+"_s2m"
            return ret
            
        return  name + " => " + str(obj)


    def _vhdl__Pull(self,obj):
        args = ""
        for x in obj.hdl_conversion__.getMemberArgsImpl(obj, InOut_t.input_t,""):
            
            args += ", " + x["vhdl_name"]

        return "    pull( " +str(obj) +args+");\n"

    def _vhdl__push(self,obj):
        args = ""
        for x in obj.hdl_conversion__.getMemberArgsImpl(obj, InOut_t.output_t,""):
            
            args += ", " + x["vhdl_name"]

        return  "    push( " +str(obj) +args+");\n"


   
    def getMemberArgsImpl(self, obj, InOut_Filter,InOut,suffix=""):
        members = obj.getMember(InOut_Filter) 
        members_args = list()
        
        for i in members:
            if i["symbol"].Inout == InOut_t.Slave_t:
                inout_local =  InoutFlip(InOut_Filter)
            else:
                inout_local = InOut_Filter 

            if issubclass(type(i["symbol"]),v_class)   and  i["symbol"].__v_classType__ == v_classType_t.Master_t:
                members_args.append( i["symbol"].hdl_conversion__.getMemberArgsImpl( i["symbol"], inout_local,InOut) )
            
            else:
                members_args.append({ 
                    "name" :  i["name"], 
                    "symbol" : i["symbol"].getType(inout_local),
                    "vhdl_name": i["symbol"].get_vhdl_name(inout_local)
                    })
            
        return members_args

    def getMemberArgs(self,obj, InOut_Filter,InOut,suffix=""):
        members = obj.getMember(InOut_Filter) 
        members_args = ""
        start = " signal "
        
        for i in members:
            if i["symbol"].Inout == InOut_t.Slave_t:
                inout_local =  InoutFlip(InOut_Filter)
            else:
                inout_local = InOut_Filter 

            if issubclass(type(i["symbol"]),v_class)   and  i["symbol"].__v_classType__ == v_classType_t.Master_t:
                members_args += start.replace("signal","") + i["symbol"].hdl_conversion__.getMemberArgs(i["symbol"], inout_local,InOut)
            
            else:
                members_args += start + i["name"] + " : " + InOut + " "  + i["symbol"].getType(inout_local)+suffix
            
            start = "; signal "
        
        return members_args    

    def getMemeber_Connect(self,obj, InOut_Filter,PushPull,ClassName=None):
        if ClassName:
            PushPullPrefix = ClassName + "."
        else:
            PushPullPrefix = ""
            
        members = obj.getMember(InOut_Filter) 
        ret = "\n"
        for x in members:
            if  issubclass(type(x["symbol"]),v_class):
                PushName = "push"
                PullName = "pull"
                if x["symbol"].Inout == InOut_t.Slave_t:
                    PushName = "push_rev"
                    PullName = "pull_rev"

                if x["symbol"].__v_classType__ == v_classType_t.Master_t:
                    if PushPull == "push":
                        varName = x["symbol"].hdl_conversion__.getMemberArgs(x["symbol"], InOut_Filter,"in")
                        varArgs = ""
                        start   = ""
                        for v in varName.split(";"):
                            varArgs +=start+ v.split(":")[0].replace("signal","")
                            start =", "

                        ret += "  "+PushName + "( self." + x["name"]  +", " + varArgs +");\n"
                
                    else:
                        varName = x["symbol"].hdl_conversion__.getMemberArgs(x["symbol"], InOut_Filter,"in")
                        varArgs = ""
                        start   = ""
                        for v in varName.split(";"):
                            varArgs +=start+ v.split(":")[0].replace("signal","")
                            start =", "

                        ret += "  "+PullName + "( self." + x["name"] + ", " + varArgs  +");\n"
        
                else:
                    if PushPull == "push":
                        ret += "  "+PushName + "( self." + x["name"]  +", " + PushPullPrefix + x["name"] +");\n"
                    else:
                        ret += "  "+PullName + "( self." + x["name"] + ", " +PushPullPrefix + x["name"] +");\n"
        
            else:
                if PushPull == "push":
                    ret += "  "+ PushPullPrefix + x["name"] +" <=  self." + x["name"]  +";\n"
                else:
                    ret += "  self." + x["name"] + " := " +PushPullPrefix + x["name"] +";\n"
        

        return ret
 
    def _vhdl__reasign(self, obj, rhs, context=None):

        asOp = obj.hdl_conversion__.get_assiment_op(obj)
        if obj.Inout == InOut_t.Slave_t:
            raise Exception("cannot assign to slave")
        elif obj.Inout == InOut_t.input_t:
            raise Exception("cannot assign to input")
        
        if rhs.Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")
        elif rhs.Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")

        if rhs.type != obj.type:
            raise Exception("cannot assigne different types.", str(obj), rhs.type, obj.type )


        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret ="---------------------------------------------------------------------\n--  " + str(obj) +" << " + str (rhs)+"\n" 
            
            ret += obj.get_vhdl_name(InOut_t.output_t) + asOp + rhs.get_vhdl_name(InOut_t.output_t) +";\n" 
            ret += rhs.get_vhdl_name(InOut_t.input_t) + asOp + obj.get_vhdl_name(InOut_t.input_t)
            return ret 

        return str(obj) + asOp +  str(rhs)



class v_class(vhdl_base):

    def __init__(self,Name,varSigConst=None):
        super().__init__()
        self.hdl_conversion__ = v_class_converter()

        self.name = Name
        self.type = Name
        self.__v_classType__ = v_classType_t.transition_t 
        self.__NameMaster__ = Name + "_master"
        self.__NameSlave__  = Name + "_slave"
        self.__NameMaster2Slave__ = Name + "_m2s"
        self.__NameSlave2Master__ = Name+"_s2m"
        self.__BeforePull__ = ""
        self.__AfterPull__  = ""
        self.__BeforePush__ = ""
        self.__AfterPush__  = ""
        self.__vectorPush__ = False
        self.__vectorPull__ = False
        self.__ast_functions__ =list()
        self.__connection__ = list()
        self.Inout  = InOut_t.Internal_t
        self.vhdl_name =None
        self.__Driver__ = None
        self._update_list = list()

        
        if not varSigConst:
            varSigConst = getDefaultVarSig()
        self.varSigConst = varSigConst

    def set_vhdl_name(self,name):
        if self.vhdl_name and self.vhdl_name != name:
            raise Exception("double Conversion to vhdl")
        else:
            self.vhdl_name = name

    def _sim_append_update_list(self,up):
        self._update_list.append(up)


    def _sim_get_value(self):
        raise Exception("not yet implemented")

    def getName(self):
        return self.name

    def get_type(self):
        return self.type

    def get_vhdl_name(self,Inout=None):
        if Inout== None:
            return self.vhdl_name
        
        if self.__v_classType__ == v_classType_t.Slave_t:
            Inout = InoutFlip(Inout)

        if Inout== InOut_t.input_t:
            return self.vhdl_name+"_s2m"
        
        elif Inout== InOut_t.output_t:
            return self.vhdl_name+"_m2s"
        return None



    def getType(self,Inout=None):
        if Inout == InOut_t.input_t:
            return self.__NameSlave2Master__
        elif Inout == InOut_t.output_t:
            return self.__NameMaster2Slave__ 
        else:    
            return self.type 

    def getTypes(self):
        return {
            "main" : self.type,
            "m2s"  : self.__NameMaster2Slave__ ,
            "s2m"  : self.__NameSlave2Master__

        }        
        




    def setInout(self,Inout):
        if self.__v_classType__ == v_classType_t.transition_t:
            self.Inout = Inout
        elif self.__v_classType__ == v_classType_t.Record_t:
            self.Inout = Inout
        elif self.__v_classType__ == v_classType_t.Master_t and Inout == InOut_t.Master_t:
            self.Inout = Inout
        elif self.__v_classType__ == v_classType_t.Slave_t and Inout == InOut_t.Slave_t:
            self.Inout = Inout    
        else:
            raise Exception("wrong combination of Class type and Inout type",self.__v_classType__,Inout)

    def set_varSigConst(self, varSigConst):
        for x  in self.getMember():
            x["symbol"].set_varSigConst(varSigConst)
                

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
            



        






    def make_serializer(self):
        pass 

    
    def getMember(self,InOut_Filter=None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if issubclass(type(t),vhdl_base) :
                if t.isInOutType(InOut_Filter):
                    ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret



    def set_simulation_param(self,module, name,writer):
        members = self.getMember() 
        for x in members:
            x["symbol"].set_simulation_param(module, name+"_"+ x["name"], writer)






 


    def getBody_onPush(self):
        for x in self.__ast_functions__:
            if x.name.lower() == "_onpush":
                return x.body

        return ""
    
    def getBody_onPull(self):
        for x in self.__ast_functions__:
            if x.name.lower() == "_onpull":
                return x.body

        return ""
 
    
  
    def __str__(self):
        if self.__Driver__ and str( self.__Driver__) != 'process':
            return str(self.__Driver__)

        if self.vhdl_name:
            return str(self.vhdl_name)

        return str(self.value)



    def _connect(self,rhs):
        if self.Inout != rhs.Inout and self.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Slave_t and self.Inout != InOut_t.Master_t:
            raise Exception("Unable to connect different InOut types")
        
        if type(self).__name__ != type(rhs).__name__:
            raise Exception("Unable to connect different types")

        

        
        self_members = self.getMember(InOut_t.input_t)
        rhs_members = rhs.getMember(InOut_t.input_t)
        for i in range(len(self_members)):
            rhs_members[i]['symbol'] << self_members[i]['symbol']
        
        self_members = self.getMember(InOut_t.output_t)
        rhs_members = rhs.getMember(InOut_t.output_t)
        for i in range(len(self_members)):
            self_members[i]['symbol'] << rhs_members[i]['symbol']



    def __lshift__(self, rhs):
        if self.__Driver__ :
            raise Exception("symbol has already a driver", str(self))
        self._connect(rhs)


  
    

    


    def Connect(self,Connections):
        self.__connection__.append(Connections)
        return self

