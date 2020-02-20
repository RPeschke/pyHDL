import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *
from CodeGen.xgenDB import *

class axisStream_converter(v_class_converter):
    def includes(self,obj, name,parent):
        typeName = obj.data.hdl_conversion__.get_type_simple(obj.data)
        
        return "use work.axisStream_"+str(typeName)+".all;\n"
    
    def get_packet_file_name(self, obj):
        typeName = obj.data.hdl_conversion__.get_type_simple(obj.data)
        return "axisStream_"+str(typeName)+".vhd"

    def get_packet_file_content(self, obj):
        typeName = obj.data.hdl_conversion__.get_type_simple(obj.data)
        pack =  "axisStream_"+str(typeName)

        fileContent = make_package(pack,  obj.data)
        return fileContent

class axisStream(v_class):
    def __init__(self,Axitype):
        super().__init__("axiStream_"+Axitype.hdl_conversion__.get_type_simple(Axitype))
        self.hdl_conversion__ =axisStream_converter()
        AddDataType(  Axitype  )
        self.valid  = port_out( v_sl() )
        self.last   = port_out( v_sl() )
        self.data   = port_out( Axitype  )
        self.ready  = port_in( v_sl() )
    

            
class axisStream_slave_converter(axisStream_converter):
    def _vhdl__to_bool(self, obj, astParser):
        return "isReceivingData(" + str(obj) + ") "

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):
        vhdl_name = str(obj) + "_buff"
        buff =  astParser.try_get_variable(vhdl_name)

        if buff == None:
            buff = v_copy(obj.rx.data)
            buff.vhdl_name = str(obj) + "_buff"
            astParser.LocalVar.append(buff)

        astParser.AddStatementBefore("read_data(" +str(obj) +", " +str(buff) +' ) ')
        return buff

    def includes(self,obj, name,parent):
        ret = obj.rx.hdl_conversion__.includes(obj.rx,None,None)
        return ret

    def get_packet_file_name(self, obj):
        ret = obj.rx.hdl_conversion__.get_packet_file_name(obj.rx)
        return ret


    def get_packet_file_content(self, obj):
        ret = obj.rx.hdl_conversion__.get_packet_file_content(obj.rx)
        return ret


class axisStream_slave(v_class):
    def __init__(self, Axi_in):
        super().__init__(Axi_in.type+"_slave")
        self.hdl_conversion__ =axisStream_slave_converter()
        self.rx = v_variable( port_Slave(Axi_in))
        self.rx  << Axi_in
     
  
        self.__v_classType__         = v_classType_t.Slave_t
        self.data_isvalid            = v_variable( v_sl() )
        self.data_internal2          = v_variable( v_copy(Axi_in.data) )
        self.data_internal_isvalid2  = v_variable( v_sl())
        self.data_internal_was_read2 =  v_variable(v_sl())
        self.data_internal_isLast2   =v_variable( v_sl())
        self.__vectorPull__ = True
        self.__vectorPush__ = True


    def observe_data(self, dataOut = port_out(dataType())):
        if self.data_internal_isvalid2:
            dataOut << self.data_internal2
    
    
    def read_data(self, dataOut = port_out(dataType())):
        if self.data_internal_isvalid2:
            dataOut << self.data_internal2
            self.data_internal_was_read2 << 1
    

    def isReceivingData(self):
        return  self.data_internal_isvalid2 == 1


    def IsEndOfStream(self):
        return  self.data_internal_isvalid2  and  self.data_internal_isLast2

    def __bool__(self):
        
        return self.isReceivingData()

    def _onPull(self):

        if self.rx.ready and self.rx.valid:
            self.data_isvalid << 1
        
        self.data_internal_was_read2 << 0
        self.rx.ready << 0      
   
        if self.data_isvalid  and not self.data_internal_isvalid2:
            self.data_internal2 << self.rx.data 
            self.data_internal_isvalid2 << self.data_isvalid
            self.data_internal_isLast2 << self.rx.last
            self.data_isvalid << 0

   
      
    def _sim_get_value(self):
        if self.data_internal_isvalid2:
            self.data_internal_was_read2 << 1

        return self.data_internal2._sim_get_value()

    def _onPush(self):
        if self.data_internal_was_read2:
            self.data_internal_isvalid2 << 0

        if not self.data_isvalid and not self.data_internal_isvalid2:
            self.rx.ready << 1



class axisStream_master_converter(axisStream_converter):
    def _vhdl__to_bool(self, obj, astParser):
        return "ready_to_send(" + str(obj) + ") "
    
    def _vhdl__reasign(self,obj, rhs):
        return "send_data( "+str(obj) + ", " +  str(rhs)+")"
    
    def includes(self,obj, name,parent):
        ret = obj.tx.hdl_conversion__.includes(obj.tx,None,None)
        return ret

    def get_packet_file_name(self, obj):
        ret = obj.tx.hdl_conversion__.get_packet_file_name(obj.tx)
        return ret

    def get_packet_file_content(self, obj):
        ret = obj.tx.hdl_conversion__.get_packet_file_content(obj.tx)
        return ret

class axisStream_master(v_class):
    def __init__(self, Axi_Out):
        super().__init__(Axi_Out.type + "_master")
        self.hdl_conversion__ =axisStream_master_converter()
        self.tx =v_variable(  port_Master(Axi_Out))
        
        self.tx.data.__Driver__ = None
        self.tx.last.__Driver__ = None
        self.tx.valid.__Driver__ = None
        self.tx.ready.__Driver__ = None


        Axi_Out  << self.tx

        
        #self.tx._connect(Axi_Out)
        self.__v_classType__         = v_classType_t.Master_t
        self.__vectorPull__ = True
        self.__vectorPush__ = True
    
   

        
    def send_data(self, dataIn = port_in(dataType())):
        self.tx.valid   << 1
        self.tx.data    << dataIn    
    
    def ready_to_send(self):
        return not self.tx.valid

    def Send_end_Of_Stream(self, EndOfStream= port_in(v_bool())):
        if EndOfStream:
            self.tx.last << 1
        else:
            self.tx.last << 0


    def _onPull(self):
        if self.tx.ready: 
            self.tx.valid << 0 
            self.tx.last  << 0  
            self.tx.data  << 0
    
    def __lshift__(self, rhs):
        self.send_data(value(rhs))

    def __bool__(self):
        
        return self.ready_to_send()



class axisStream_slave_signal_converter(axisStream_converter):
    def includes(self,obj, name,parent):
        ret = obj.rx.hdl_conversion__.includes(obj.rx,None,None)
        return ret

    def get_packet_file_name(self, obj):
        ret = obj.rx.hdl_conversion__.get_packet_file_name(obj.rx)
        return ret

    def get_packet_file_content(self, obj):
        ret = obj.rx.hdl_conversion__.get_packet_file_content(obj.rx)
        return ret

class axisStream_slave_signal(v_class):
    def __init__(self, Axi_Out):
        super().__init__(Axi_Out.type + "_master_signal")
        self.__v_classType__         = v_classType_t.Master_t
        self.hdl_conversion__ =axisStream_slave_signal_converter()
        self.rx = signal_port_Slave(Axi_Out)
        self.rx << Axi_Out

        self.internal       = v_signal(Axi_Out)
        self.v_internal     = v_variable(Axi_Out)
        self.v_internal << self.internal
        



#    @architecture
#    def connect(self):
#        @combinational()
#        def p1():
#            self.rx.ready       << v_switch(0, 
#                [v_case( self.rx.valid and self.internal.ready , 1)]
#                )
#            self.internal.data  << self.rx.data
#            self.internal.last  << self.rx.last
#            self.internal.valid << self.rx.valid



class axisStream_master_with_strean_counter(v_class):
    def __init__(self, Axi_in):
        super().__init__(Axi_in.type + "_master_with_counter")
        self.AxiTX = port_Master(axisStream_master(Axi_in))
        self.__v_classType__         = v_classType_t.Master_t
        self.Counter = v_int(0)
        self.SendingData = v_sl()
        self.EndOfStream = v_sl()
        self.EOF_Counter_max = v_int(0)


        self.__BeforePush__ ='''
        if self.SendingData = '1' then
            self.counter := self.counter + 1;
        end if;
       
        if self.SendingData = '1' and self.counter = 0 and self.EndOfStream ='1' then
            
            Send_end_Of_Stream(self.AxiTX);
            self.EndOfStream :='0';
            
        elsif  self.SendingData = '1' and self.counter > 0 and self.EndOfStream ='1' then
            self.counter := self.EOF_Counter_max;
        end if;

        self.SendingData := '0';
        '''
        self.ready_to_send = v_function(returnType="boolean",body = '''
        return ready_to_send(self.AxiTX); 
        ''')
        self.ready_to_send_at_pos = v_function(argumentList="position : integer", returnType="boolean",body = '''
        if self.counter = position then
            return ready_to_send(self); 
        end if;

        return false;
        ''')
        
        self.send_data = v_procedure(argumentList= "datain : in " + self.AxiTX.tx.data.type, body='''
        if ready_to_send(self) then
            send_data(self.AxiTX,datain);
            self.SendingData := '1';
        end if;
   ''')
        self.Send_end_Of_Stream = v_procedure(argumentList= "EndOfStream : in boolean := true",body='''
        if EndOfStream then
            self.EndOfStream := '1';
        else
            self.EndOfStream := '0';
        end if;
        
   
''')

        self.send_data_at = v_procedure(argumentList= "position : integer ;  datain : in " + self.AxiTX.tx.data.type , body='''
        if ready_to_send_at_pos(self, position) then
            send_data(self, datain);
        end if;
        
        if position < self.EOF_Counter_max then
            self.EOF_Counter_max := position;
        end if;
   ''')
        self.send_data_begining_at = v_procedure(argumentList= "position : integer ;  datain : in " + self.AxiTX.tx.data.type , body='''
        if ready_to_send_begining_at(self,position) then
            send_data(self, datain);
        end if;
        
        if position < self.EOF_Counter_max then
            self.EOF_Counter_max := position;
        end if;
   ''')
        self.ready_to_send_begining_at = v_function(argumentList="position : integer", returnType="boolean",body = '''
        if self.counter >= position  then
            return ready_to_send(self); 
        end if;
        return false;
        ''')



class  axiStream_package(v_package):
    def __init__(self,PackageName, AXiName):
        super().__init__(PackageName)
        if AXiName.isdigit():
            AxiType = v_slv(int(AXiName))
        else:
            pac = get_package_for_type(AXiName)
            if  pac:
                include = pac["packageDef"][0]
                include =  "use work."+include+".all;\n"

            else:
                include= "-- Unable to locate package which contains class: '" +AXiName+"'  $$$missingInclude$$$"
            AxiType = v_symbol(AXiName,AXiName+"_null", includes = include)

        self.axi = axisStream(AXiName,AxiType)
        self.axi_slave = axisStream_slave(AXiName,AxiType)
        self.axi_master = axisStream_master(AXiName,AxiType)
        self.axisStream_master_with_strean_counter =axisStream_master_with_strean_counter(AXiName,AxiType)
 


def arg2type(AXiName):
    if AXiName.isdigit():
        AxiType = v_slv(int(AXiName))
    else:
        pac = get_package_for_type(AXiName)
        if  pac:
            include = pac["packageDef"][0]
            include =  "use work."+include+".all;\n"

        else:
            include= "-- Unable to locate package which contains class: '" +AXiName+"'  $$$missingInclude$$$"
        AxiType = v_symbol(AXiName,AXiName+"_null", includes = include)

    return AXiName,AxiType


def make_package(PackageName,AxiType):
    s = isConverting2VHDL()
    set_isConverting2VHDL(True)

    ax_t = axisStream(AxiType)
    ax = v_package(PackageName,sourceFile=__file__,
    PackageContent = [
        ax_t,
        axisStream_slave(ax_t),
        axisStream_master(ax_t),
       # axisStream_slave_signal(ax_t)
        axisStream_master_with_strean_counter(ax_t)
    ]
    
    
    )
    fileContent = ax.to_string()
    set_isConverting2VHDL(s)
    return fileContent

def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_axiStream_32.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_axistream_32_SD")

    args = parser.parse_args()
    sp = args.PackageName.split("_")
    AXiName,AxiType = arg2type(sp[2])
    fileContent = make_package(args.PackageName,AXiName ,AxiType)

    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)
        


if __name__== "__main__":
    main()

