import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
    from CodeGen.xgen_v_function import *
    from CodeGen.xgen_v_entity_list import *
    from CodeGen.xgen_simulation import *
else:
    from .xgenBase import * 
    from .xgen_v_function import *
    from .xgen_v_entity_list import *
    from .xgen_simulation import *


def _get_connector(symb):
    if symb.Inout == InOut_t.Master_t:
        n_connector = symb.__receiver__[-1]
    else :
        n_connector = symb.__Driver__
    
    return n_connector

class v_class_converter(vhdl_converter_base):
    def __init__(self):
        super().__init__()
        self.__BeforePull__ = ""
        self.__AfterPull__  = ""
        self.__BeforePush__ = ""
        self.__AfterPush__  = ""
        self.__ast_functions__ =list()

    def includes(self,obj, name,parent):
        ret = ""
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base):
                        
                ret += t.hdl_conversion__.includes(t,x[0],obj)
        
        for x in obj.hdl_conversion__.__ast_functions__:
            ret += x.hdl_conversion__.includes(x,None,obj)

        ret += "use work."+obj.hdl_conversion__.get_type_simple(obj)+"_pack.all;"
        return ret

    def get_packet_file_name(self, obj):
        if obj.__vetoHDLConversion__  == True:
            return ""
        return obj.hdl_conversion__.get_type_simple(obj)+"_pack.vhd"

    def get_packet_file_content(self, obj):
        if obj.__vetoHDLConversion__  == True:
            return ""
        PackageName = obj.hdl_conversion__.get_type_simple(obj)+"_pack"
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        
        
        obj.hdl_conversion__.parse_file(obj)
        
        
        ret = "-- XGEN: Autogenerated File\n\n"
        inc = obj.hdl_conversion__.includes(obj, None, obj)
        ret += make_unique_includes(inc,obj.hdl_conversion__.get_type_simple(obj)+"_pack")
        ret += "\n\n"
        p_header = obj.hdl_conversion__.getHeader(obj,None, None)
        if p_header.strip():
            ret += "package " + PackageName + " is \n\n"
            ret += p_header
            ret += "end " + PackageName + ";\n\n\n"

            ret += "package body "+ PackageName +" is\n\n"
            ret += obj.hdl_conversion__.getBody(obj,None, None)
            ret += "end "+ PackageName +";\n\n"
        
        ret += obj.hdl_conversion__.get_entity_definition(obj)

        set_isConverting2VHDL(s)
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

    def make_constant(self, obj, name,parent=None,InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = obj.getType()
        member = obj.getMember()
       
        start = "\n  constant " + name + " : " + TypeName + ":= (\n  "

        Content = [
            x["symbol"].hdl_conversion__.recordMemberDefault(x["symbol"], x["name"],obj,InOut_Filter) 
            for x in member
        ]
        ret=join_str(Content,start= start ,end=  "\n  );\n",Delimeter=",\n    ", IgnoreIfEmpty=True)

        return ret

    def getHeader(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        ret = "-------------------------------------------------------------------------\n"
        ret += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        
        ts = obj.hdl_conversion__.extract_conversion_types(obj)
        for t in ts:
            ret +=  obj.hdl_conversion__.getHeader_make_record(t["symbol"], name,parent,t["symbol"].Inout ,t["symbol"].varSigConst)
            ret += "\n\n"
        
        obj.hdl_conversion__.make_connection(obj,name,parent)
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base) and not issubclass(type(t),v_class):
                ret += t.hdl_conversion__.getHeader(t,x[0],obj)

        funlist =[]
        for x in reversed(obj.hdl_conversion__.__ast_functions__):
            if "_onpull" in x.name.lower()  or "_onpush" in x.name.lower() :
                continue
            funDeclaration = x.hdl_conversion__.getHeader(x,None,None)
            if funDeclaration in funlist:
                x.isEmpty = True
                continue
            funlist.append(funDeclaration)
            ret +=  funDeclaration


        ret += "------- End Psuedo Class " +obj.getName() +" -------------------------\n"
        ret += "-------------------------------------------------------------------------\n\n\n"
        return ret


    def getHeader_make_record(self,obj, name, parent=None, InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = obj.getType()
        member = obj.getMember()
        start= "\ntype "+TypeName+" is record \n"
        end=  """end record;
    
    {Default}

    type {TypeName}_a is array (natural range <>) of {TypeName};
        """.format(
          Default = obj.hdl_conversion__.make_constant(
                obj,
                TypeName+ "_null", 
                parent, 
                InOut_Filter,
                VaribleSignalFilter
              ),
          TypeName=TypeName  
        )

        
        Content = [
            x["symbol"].hdl_conversion__.recordMember(x["symbol"],x["name"],obj,InOut_Filter)
            for x in member
        ]
        ret=join_str(Content,start= start ,end= end, IgnoreIfEmpty=True)


        return ret

    def make_connection(self, obj, name, parent):
            
        
        if obj.__v_classType__ == v_classType_t.transition_t:    
            obj.pull          =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "pull", procedureName="pull" )
            obj.push          =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "push", procedureName="push")
            obj.pull_rev      =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "pull", procedureName="pull")
            obj.push_rev      =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "push", procedureName="push")
            
        elif obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
   
            obj.pull       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.input_t , "pull")
            obj.push       =  obj.hdl_conversion__.getConnecting_procedure(obj, InOut_t.output_t, "push")

            if obj.__vectorPull__:
                obj.vpull       =  obj.hdl_conversion__.getConnecting_procedure_vector(obj, InOut_t.input_t , "pull",procedureName="pull")
            if obj.__vectorPush__:
                obj.vpush       =  obj.hdl_conversion__.getConnecting_procedure_vector(obj, InOut_t.output_t, "push",procedureName="push")

        elif obj.__v_classType__ == v_classType_t.Record_t:
            obj.pull       =  obj.hdl_conversion__.getConnecting_procedure_record(obj, "pull")
            obj.push       =  obj.hdl_conversion__.getConnecting_procedure_record(obj, "push")


    def getConnecting_procedure_record(self,obj, PushPull):
        
        if PushPull== "push":
            inout = " out "
            line =  "data_IO  <=  self;"
        else:
            inout = " in "
            line =  "self  := data_IO;"


        TypeName = obj.getType()
        args = "self : inout "+ TypeName + "; signal data_IO : " + inout + " " + TypeName

        ret = v_procedure(
            name=None, 
            argumentList=args , 
            body=line,
            isFreeFunction=True,
            IsEmpty=False
            )

        return ret
    def getConnecting_procedure_vector(self,obj, InOut_Filter,PushPull,procedureName=None):
        
        isEmpty = False
        if PushPull== "push":
            inout = " out "
            isEmpty = obj.push.isEmpty

        else:
            inout = " in "
            isEmpty = obj.pull.isEmpty
       
        argumentList =  obj.hdl_conversion__.getMemberArgs(obj, InOut_Filter,inout,suffix="_a",IncludeSelf = True).strip()

        
        xs = obj.hdl_conversion__.extract_conversion_types(obj )
        content = []
             

        for x in xs:
            line = "self" + x["suffix"] +" =>  self" + x["suffix"]+"(i)"
            content.append(line)
        selfargout =join_str(content,
            Delimeter= ", ",
            IgnoreIfEmpty=True
            )

        members = obj.getMember(InOut_Filter) 
        args=join_str([
                str(x["name"]) +" => " + str(x["name"]+"(i)")
                for x in members
            ],
            LineBeginning= ", ",
            IgnoreIfEmpty=True
            )

            
        ret        = v_procedure(name=procedureName, argumentList=argumentList , body='''
        for i in 0 to self'length - 1 loop
        {PushPull}({selfargout} {args});
        end loop;
            '''.format(
                PushPull=PushPull,
                args = args,
                selfargout=selfargout
            ),
            isFreeFunction=True,
            IsEmpty=isEmpty
            )

        return ret

    def getBody_onPush(self, obj):
        for x in obj.hdl_conversion__.__ast_functions__:
            if "_onpush" in x.name.lower():
                return x.body
        return ""

    def getBody_onPull(self, obj):
        for x in obj.hdl_conversion__.__ast_functions__:
            if  "_onpull" in x.name.lower() :
                return x.body
        return ""


    def getConnecting_procedure(self,obj, InOut_Filter,PushPull, procedureName=None):
        ClassName=None
        beforeConnecting = ""
        AfterConnecting = ""
        classType = obj.getType(InOut_Filter)
        isFreeFunction = False
        
        if PushPull== "push":
            beforeConnecting = obj.hdl_conversion__.getBody_onPush(obj)
            inout = " out "
        else:
            AfterConnecting = obj.hdl_conversion__.getBody_onPull(obj)
            inout = " in "
            
            

        if  obj.__v_classType__ == v_classType_t.transition_t:
            ClassName="IO_data"
            argumentList = "signal " + ClassName +" : " + inout+ classType
        else:
            argumentList = obj.hdl_conversion__.getMemberArgs(obj, InOut_Filter,inout,IncludeSelf = True)
            isFreeFunction = True

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
            IsEmpty=IsEmpty,
            isFreeFunction=isFreeFunction
            )
        
        return ret

    def getBody(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        start  = "-------------------------------------------------------------------------\n"
        start += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        end  = "------- End Psuedo Class " +obj.getName() +" -------------------------\n  "
        end += "-------------------------------------------------------------------------\n\n\n"
  
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),vhdl_base):
                start += t.hdl_conversion__.getBody(t,x[0],obj)

        content2 =  [
            x.hdl_conversion__.getBody(x,None,None) 
            for x in obj.hdl_conversion__.__ast_functions__ 
            if not ("_onpull" in x.name.lower()   or  "_onpush" in x.name.lower() )
        ]


        ret=join_str(content2, start=start,end=end)
        
        

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
        ret = []
        xs = obj.hdl_conversion__.extract_conversion_types(obj)
        for x in xs:
            if  x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            if obj.Inout != InOut_t.Internal_t and obj._isInstance == False:
                continue
            if x["symbol"].varSigConst == varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"].varSigConst)

            ret.append(VarSymb + " " +x["symbol"].get_vhdl_name() + " : " + x["symbol"].type+" := " + x["symbol"].type+"_null")

        ret=join_str(
            ret, 
            LineEnding=";\n",
            LineBeginning="  "
            )
        return ret
        

    def get_port_list(self,obj):
        ret = []
        xs = obj.hdl_conversion__.extract_conversion_types(obj)
        for x in xs:
            if x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            inoutstr = " : "+ x["symbol"].hdl_conversion__.InOut_t2str(x["symbol"]) +" "
            ret.append( x["symbol"].get_vhdl_name()+ inoutstr +x["symbol"].type + " := " + x["symbol"].type + "_null")
    
        return ret


    def _vhdl_make_port(self, obj, name):
        ret = []

        xs =obj.hdl_conversion__.extract_conversion_types(obj, 
                exclude_class_type= v_classType_t.transition_t
            )
        for x in xs:
            ret.append( name + x["suffix"] + " => " + x["symbol"].get_vhdl_name())

        return ret


           
    

    def __vhdl__Pull_Push(self, obj, Inout):
        if obj.__v_classType__  == v_classType_t.Record_t:
            return ""
        selfHandles = []
        xs = obj.hdl_conversion__.extract_conversion_types(obj)
        for x in xs:
            arg = "self"+x["suffix"] + "  =>  " +str(obj) + x["suffix"]
            selfHandles.append(arg)

        
        content = []
        for x in obj.getMember( Inout,varSig.variable_t):
            n_connector = _get_connector( x["symbol"])
            

            ys =n_connector.hdl_conversion__.extract_conversion_types(n_connector, 
                    exclude_class_type= v_classType_t.transition_t, filter_inout=Inout
                )
            for y in ys:
                content.append(x["name"]+" => "+y["symbol"].get_vhdl_name())
        
        #content = [ 
        #    x["name"]+" => "+x["symbol"].hdl_conversion__._get_connector_name(x["symbol"], Inout)
        #    for x in obj.getMember( Inout,varSig.variable_t) 
        #]

        pushpull= "push"
        if Inout == InOut_t.input_t:
            pushpull = "pull"

        ret=join_str(
            selfHandles+content, 
            start="    " + pushpull + "( ",
            end=");\n",
            Delimeter=", "
            )

        return ret        
        
    def _vhdl__Pull(self,obj):

        return obj.hdl_conversion__.__vhdl__Pull_Push(obj,InOut_t.input_t)

    def _vhdl__push(self,obj):


        return obj.hdl_conversion__.__vhdl__Pull_Push(obj,InOut_t.output_t)



   
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

    def getMemberArgs(self,obj, InOut_Filter,InOut,suffix="", IncludeSelf =False):
        members_args = []
        
        if IncludeSelf:
            xs = obj.hdl_conversion__.extract_conversion_types(obj )
            for x in xs:
                varsig = " "
                self_InOut = " inout "
                if x["symbol"].varSigConst == varSig.signal_t :
                    varsig = " signal "
                    self_InOut = " in "  
                members_args.append(varsig + "self" + x["suffix"]  + " : " + self_InOut + " "  + x["symbol"].getType()+suffix)
        
        members = obj.getMember(InOut_Filter) 
       
        for i in members:
            n_connector = _get_connector( i["symbol"])
            xs = i["symbol"].hdl_conversion__.extract_conversion_types( i["symbol"], 
                    exclude_class_type= v_classType_t.transition_t, filter_inout=InOut_Filter
                )

            for x in xs:
               
                varsig = " "
                if n_connector.varSigConst == varSig.signal_t :
                    varsig = " signal "
                    
                members_args.append(varsig + i["name"] + " : " + InOut + " "  + x["symbol"].getType()+suffix)
            

        ret=join_str(
            members_args, 
            Delimeter="; "
            )
        return ret    

    def getMemeber_Connect(self,obj, InOut_Filter,PushPull,ClassName=None):
        if ClassName:
            PushPullPrefix = ClassName + "."
        else:
            PushPullPrefix = ""
            
        members = obj.getMember() 
        ret = "\n"
        for x in members:
            ys =x["symbol"].hdl_conversion__.extract_conversion_types(
                x["symbol"],
                exclude_class_type= v_classType_t.transition_t,
                filter_inout=InOut_Filter)
            for y in ys:
                ret += "  " + PushPull+"(self." + x["name"]+", "+PushPullPrefix + x["name"] +");\n"
        return ret      
         
 
    def _vhdl__reasign(self, obj, rhs, context=None,context_str=None):
        
        asOp = obj.hdl_conversion__.get_assiment_op(obj)

        
        if rhs.Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")
        elif rhs.Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")

        if rhs.type != obj.type:
            raise Exception("cannot assigne different types.", str(obj), rhs.type, obj.type )

        
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret ="---------------------------------------------------------------------\n--  " + obj.get_vhdl_name() +" << " + rhs.get_vhdl_name()+"\n" 
            
            ret += obj.get_vhdl_name(InOut_t.output_t) + asOp + rhs.get_vhdl_name(InOut_t.output_t) +";\n" 
            ret += rhs.get_vhdl_name(InOut_t.input_t) + asOp + obj.get_vhdl_name(InOut_t.input_t)
            return ret 

        obj._add_output()
        return obj.get_vhdl_name() + asOp +  rhs.get_vhdl_name()

    def get_self_func_name(self, obj, IsFunction = False, suffix = ""):
        xs = obj.hdl_conversion__.extract_conversion_types(obj ,filter_inout=InOut_t.Internal_t)
        content = []
             

        for x in xs:
            inout = " inout "
            if x["symbol"].__v_classType__ == v_classType_t.transition_t:
                pass
            elif x["symbol"].varSigConst != varSig.variable_t:
                inout = " in "

            if IsFunction:
                inout = "  "
                

            
            line = "self" +x["suffix"] + " : " + inout + x["symbol"].get_type()  + suffix
            content.append(line)

        
        
        ret=join_str(
            content, 
            Delimeter="; "
            )
        
        return ret


    def _vhdl_get_attribute(self,obj, attName):
        attName = str(attName)
        if obj.__v_classType__ == v_classType_t.transition_t and obj.varSigConst != varSig.variable_t:
            for x in obj.getMember():
                if x["name"] == attName:

                    if x["symbol"].Inout  == InOut_t.output_t:
                        suffix = "_m2s"
                    else:
                        suffix = "_s2m"

                    return obj.get_vhdl_name() + suffix + "." +   attName
        
        if obj.varSigConst == varSig.combined_t:
            xs = obj.hdl_conversion__.extract_conversion_types(obj)
        else:
            xs =[{
                'suffix' : "",
                'symbol' : obj
            }]
            
        for x in xs:
            for y in x["symbol"].getMember():
                if y["name"] == attName:
                    return obj.get_vhdl_name() + x["suffix"] + "." +   attName


           
        return obj.get_vhdl_name() + "." +str(attName)
   
    def get_process_header(self,obj):

        
        ret = ""
        if obj.Inout != InOut_t.Internal_t:
            return ""
        
        xs = obj.hdl_conversion__.extract_conversion_types(obj)
        for x in xs:
            if x["symbol"].varSigConst != varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"].varSigConst)
            ret += VarSymb +" " +str(x["symbol"]) + " : " +x["symbol"].type +" := " + x["symbol"].type +"_null;\n"

        return ret

    def get_NameMaster(self,obj):
        return obj.type + "_master"

    def get_NameSlave(self,obj):
        return obj.type + "_slave"


    def get_NameMaster2Slave(self,obj):
        return obj.type + "_m2s"

    def get_NameSlave2Master(self,obj):
        return obj.type + "_s2m"

    def get_NameSignal(self,obj):
        return obj.type + "_sig"

    def get_type_simple(self,obj):
        return obj.type

    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):
        ret =[]
        
        if obj.__v_classType__ ==  v_classType_t.transition_t:
            
            
            x = v_class(obj.hdl_conversion__.get_NameSlave2Master(obj), obj.varSigConst)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x.vhdl_name = str(obj.vhdl_name)+"_s2m"

            x.Inout=InOut_t.input_t
            if obj.Inout == InOut_t.input_t or obj.Inout == InOut_t.Slave_t:
                x.Inout=InOut_t.output_t

            ys= obj.getMember(InOut_t.input_t)
            for y in ys: 
                setattr(x, y["name"], y["symbol"])
            ret.append({ "suffix":"_s2m", "symbol": x})

            x = v_class(obj.hdl_conversion__.get_NameMaster2Slave(obj), obj.varSigConst)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x.Inout=InOut_t.output_t
            
            if obj.Inout == InOut_t.input_t or obj.Inout == InOut_t.Slave_t:
                x.Inout=InOut_t.input_t
                
            x.vhdl_name = str(obj.vhdl_name)+"_m2s"
            ys= obj.getMember(InOut_t.output_t)
            for y in ys: 
                setattr(x, y["name"], y["symbol"])
            ret.append({ "suffix":"_m2s", "symbol": x})

            ret.append({ "suffix":"", "symbol": obj})
        
        elif obj.__v_classType__ ==  v_classType_t.Master_t or obj.__v_classType__ ==  v_classType_t.Slave_t: 
            x = v_class(obj.hdl_conversion__.get_NameSignal(obj), varSig.signal_t)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x.Inout= obj.Inout
            x._writtenRead = obj._writtenRead
            x.vhdl_name = obj.vhdl_name+"_sig"
            ys= obj.getMember(VaribleSignalFilter=varSig.signal_t)
            if len(ys)>0:
                for y in ys: 
                    setattr(x, y["name"], y["symbol"])
                
                ret.append({ "suffix":"_sig", "symbol": x})

            x = v_class(obj.type, varSig.variable_t)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x.Inout= obj.Inout
            x._writtenRead = obj._writtenRead
            x.vhdl_name = obj.vhdl_name
            ys= obj.getMember(VaribleSignalFilter=varSig.variable_t)
            if len(ys)>0:
                for y in ys: 
                    setattr(x, y["name"], y["symbol"])
                ret.append({ "suffix":"", "symbol": x})

            #ret.append({ "suffix":"", "symbol": obj})
        else:
            ret.append({ "suffix":"", "symbol": obj})

        ret1 = []
         
        for x in ret:
            if x["symbol"]._issubclass_("v_class")  and exclude_class_type and x["symbol"].__v_classType__ == exclude_class_type:
                continue
            if filter_inout and x["symbol"].Inout != filter_inout:
                continue           
            ret1.append(x)
        return ret1
            
class v_class(vhdl_base):

    def __init__(self,Name,varSigConst=None):
        super().__init__()
        self.hdl_conversion__ = v_class_converter()

        self.name = Name
        self.type = Name
        self.__v_classType__ = v_classType_t.transition_t 


        self.__vectorPush__ = False
        self.__vectorPull__ = False
        self.__vetoHDLConversion__ = False
        
        self.vhdl_name =None
        self.__Driver__ = None


        
        if not varSigConst:
            varSigConst = getDefaultVarSig()
        self.varSigConst = varSigConst

    def set_vhdl_name(self,name, Overwrite = False):
        if self.vhdl_name and self.vhdl_name != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        
        self.vhdl_name = name

        mem = self.getMember()
        for x in mem:
            x["symbol"].set_vhdl_name(name+"."+x["name"],Overwrite)


    def _sim_append_update_list(self,up):
        for x  in self.getMember():
            x["symbol"]._sim_append_update_list(up)


    def _sim_get_value(self):
        return self
        raise Exception("not yet implemented")

    def getName(self):
        return self.name

    def get_type(self):
        return self.type

    def get_vhdl_name(self,Inout=None):
        if Inout== None:
            return str(self.vhdl_name)
        
        if self.__v_classType__ == v_classType_t.Slave_t:
            Inout = InoutFlip(Inout)

        if Inout== InOut_t.input_t:
            return str(self.vhdl_name)+"_s2m"
        
        elif Inout== InOut_t.output_t:
            return str(self.vhdl_name)+"_m2s"
        return None



    def getType(self,Inout=None,varSigType=None):
        if self.__v_classType__ == v_classType_t.Record_t:
             return self.type 
        if Inout == InOut_t.input_t:
            return self.hdl_conversion__.get_NameSlave2Master(self)
        elif Inout == InOut_t.output_t:
            return self.hdl_conversion__.get_NameMaster2Slave(self)
        elif varSigType== varSig.signal_t:
            return self.hdl_conversion__.get_NameSignal(self) 
        else:    
            return self.type 

    def getTypes(self):
        return {
            "main" : self.type,
            "m2s"  : self.hdl_conversion__.get_NameMaster2Slave(self),
            "s2m"  : self.hdl_conversion__.get_NameSlave2Master(self)

        }        
        


    def flipInout(self):
        self.Inout = InoutFlip(self.Inout)
        members = self.getMember()
        for x in members:
            x["symbol"].flipInout()

    def resetInout(self):
        if self.Inout == InOut_t.Slave_t:
            self.flipInout()
        elif self.Inout == InOut_t.input_t:
            self.flipInout()
            
        self.Inout = InOut_t.Internal_t


    def setInout(self,Inout):
        if self.Inout == Inout:
            return 
        elif self.__v_classType__ == v_classType_t.transition_t :
            self.Inout = Inout
        elif self.__v_classType__ == v_classType_t.Record_t  and Inout == InOut_t.Master_t:
            self.Inout = InOut_t.output_t
        elif self.__v_classType__ == v_classType_t.Record_t and Inout == InOut_t.Slave_t:
            self.Inout = InOut_t.input_t
        elif self.__v_classType__ == v_classType_t.Record_t:
            self.Inout = Inout
        
        elif self.__v_classType__ == v_classType_t.Master_t and Inout == InOut_t.Master_t:
            self.Inout = Inout
        elif self.__v_classType__ == v_classType_t.Slave_t and Inout == InOut_t.Slave_t:
            self.Inout = Inout    
        else:
            raise Exception("wrong combination of Class type and Inout type",self.__v_classType__,Inout)

        if Inout == InOut_t.Internal_t:
            Inout = InOut_t.Master_t 
        members = self.getMember()
        for x in members:
            x["symbol"].setInout(Inout)


    def set_varSigConst(self, varSigConst):
        self.varSigConst = varSigConst
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
            

    def isVarSigType(self, varSigType):
        if varSigType == None:
            return True

        return self.varSigConst == varSigType

        



    def get_master(self):
        raise Exception("Function not implemented")

    def get_slave(self):
        raise Exception("Function not implemented")


    def make_serializer(self):
        pass 

    
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if not issubclass(type(t),vhdl_base) :
                continue 
            if not t.isInOutType(InOut_Filter):
                continue
            if x[0] == '__Driver__':
                continue
            if not t.isVarSigType(VaribleSignalFilter):
                continue

            ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret



    def set_simulation_param(self,module, name,writer):
        members = self.getMember() 
        for x in members:
            x["symbol"].set_simulation_param(module+"."+name, x["name"], writer)
  
    def __str__(self):
        if self.__Driver__ and str( self.__Driver__) != 'process':
            return str(self.__Driver__)

        if self.vhdl_name:
            return str(self.vhdl_name)

        return str(self.value)



    def _connect(self,rhs):
        if self.Inout != rhs.Inout and self.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Slave_t and self.Inout != InOut_t.Master_t and self.Inout != InOut_t.input_t and self.Inout != InOut_t.output_t:
            raise Exception("Unable to connect different InOut types")
        
        if type(self).__name__ != type(rhs).__name__:
            raise Exception("Unable to connect different types")
        
        self.__Driver__ = rhs
        rhs.__receiver__.append(self)

        self_members_s2m  = self.get_s2m_signals()
        rhs_members_s2m  = rhs.get_s2m_signals()

        for i in range(len(self_members_s2m)):
            rhs_members_s2m[i]['symbol'] << self_members_s2m[i]['symbol']

        self_members  = self.get_m2s_signals()
        rhs_members  = rhs.get_m2s_signals()
        for i in range(len(self_members)):
            self_members[i]['symbol'] << rhs_members[i]['symbol']

    def _connect_running(self,rhs):
        if self.Inout != rhs.Inout and self.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Internal_t and rhs.Inout != InOut_t.Slave_t and self.Inout != InOut_t.Master_t and self.Inout != InOut_t.input_t and self.Inout != InOut_t.output_t:
            raise Exception("Unable to connect different InOut types")
        
        rhs = rhs._sim_get_value()

        if type(self).__name__ != type(rhs).__name__:
            raise Exception("Unable to connect different types")
        
        
        self_members  = self.get_s2m_signals()
        rhs_members  = rhs.get_s2m_signals()

        for i in range(len(self_members)):
            rhs_members[i]['symbol'] << self_members[i]['symbol']

        self_members  = self.get_m2s_signals()
        rhs_members  = rhs.get_m2s_signals()
        for i in range(len(self_members)):
            self_members[i]['symbol'] << rhs_members[i]['symbol']

    def __lshift__(self, rhs):
        if gsimulation.isRunning():
            self._connect_running(rhs)
        else:
            if self.__Driver__ and not isConverting2VHDL():
                raise Exception("symbol has already a driver", self.get_vhdl_name())
            self._connect(rhs)


    def _get_Stream_input(self):
        return  self

    def _get_Stream_output(self):
        return self
    
    def __or__(self,rhs):
        
        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
        
        ret = v_entity_list()


        ret.append(self)
        ret.append(rhs)

        rhs_StreamIn << self_StreamOut
        return ret
        
    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_class" == test
    
    def _instantiate_(self):
        self_members = self.getMember()
        for x in self_members:
            x["symbol"]._instantiate_()

        self.Inout = InoutFlip(self.Inout)
        self._isInstance = True
        return self

    def get_m2s_signals(self):
        linput = InOut_t.input_t
        louput = InOut_t.output_t




        if self.__v_classType__ ==v_classType_t.Record_t :
            self_members = self.getMember()
            return self_members
                
        elif  self.Inout == InOut_t.Master_t:
            self_members = self.getMember(louput)
            return self_members
            
        elif  self.Inout == InOut_t.Slave_t:
            self_members = self.getMember(linput)
            return self_members
        elif  self.Inout == InOut_t.Internal_t:
            self_members = self.getMember(louput)
            return self_members            
        
    def get_s2m_signals(self):
        linput = InOut_t.input_t
        louput = InOut_t.output_t



        if self.__v_classType__ ==v_classType_t.Record_t:
            
            return []
        
        elif  self.Inout == InOut_t.Master_t:
            self_members = self.getMember(linput)
            return self_members
            
        elif  self.Inout == InOut_t.Slave_t:
            self_members = self.getMember(louput)
            return self_members
        elif  self.Inout == InOut_t.Internal_t:
            self_members = self.getMember(linput)
            return self_members      
            
    def to_arglist(self,name,parent,withDefault = False):
        ret = []
        
        xs = self.hdl_conversion__.extract_conversion_types(self)

        for x in xs:
            inoutstr = ""
            varSignal = "signal "
            if x["symbol"].varSigConst == varSig.variable_t:
                inoutstr = self.hdl_conversion__.InOut_t2str(self)
                varSignal = ""
            Default_str = ""
            if withDefault:
                Default_str =  " := " + self.hdl_conversion__.get_default_value(self)

            ret.append(varSignal + name + x["suffix"] + " : " + inoutstr +" " +  x["symbol"].getType() +Default_str)

            if x["symbol"].varSigConst == varSig.signal_t:
                members = x["symbol"].getMember()
                for m in members:
                    if m["symbol"].Inout == InOut_t.Internal_t and m["symbol"]._writtenRead == InOut_t.Internal_t:
                        continue
                    ret.append(m["symbol"].to_arglist(name + x["suffix"]+"_"+m["name"],None ,withDefault=withDefault))

                

 

        r =join_str(ret,Delimeter="; ",IgnoreIfEmpty=True)
        return r

    def _remove_drivers(self):
        self.__Driver__ = None
        mem = self.getMember()
        for x in mem:
            x["symbol"]._remove_drivers()

class v_class_master(v_class):

    def __init__(self,Name,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self.__v_classType__  = v_classType_t.Master_t
        self.varSigConst       = varSig.combined_t


class v_class_slave(v_class):

    def __init__(self,Name,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self.__v_classType__  = v_classType_t.Slave_t
        self.varSigConst       = varSig.combined_t


def get_master(transObj):
    return transObj.get_master()

def get_salve(transObj):
    return transObj.get_slave()