import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *
from CodeGen.xgenDB import *


class axisStream(v_class):
    def __init__(self,AxiName,Axitype):


        
        super().__init__("axisStream_"+str(AxiName))

        self.valid  = port_out( v_sl() )
        self.last   = port_out( v_sl() )
        self.data   = port_out(copy.deepcopy( Axitype) )
        self.ready  = port_in( v_sl() )
    



class axisStream_slave(v_class):
    def __init__(self, AXiName,AxiType):
        super().__init__("axisStream_"+ str(AXiName)+"_slave")
        self.rx = port_Slave(axisStream(AXiName,AxiType))
        self.__v_classType__         = v_classType_t.Slave_t
        self.data_isvalid            = v_sl()
        self.data_internal2          = copy.deepcopy( AxiType)
        self.data_internal_isvalid2  = v_sl()
        self.data_internal_was_read2 = v_sl()
        self.data_internal_isLast2   = v_sl()
        self.__vectorPull__ = True
        self.__vectorPush__ = True

        self.observe_data = v_procedure(argumentList= "datain : out " + self.rx.data.type, body='''
    if(self.data_internal_isvalid2 = '1') then
        datain := self.data_internal2;
    end if;
''')
        self.read_data = v_procedure(argumentList= "datain : out " + self.rx.data.type, body='''
    if(self.data_internal_isvalid2 = '1') then
        datain := self.data_internal2;
        self.data_internal_was_read2 :='1';
    end if;
''')
        
        self.isReceivingData = v_function(returnType="boolean",body = '''
    return  self.data_internal_isvalid2 = '1' ;
''')
        self.IsEndOfStream = v_function(returnType="boolean",body='''
    return  self.data_internal_isvalid2 = '1' and  self.data_internal_isLast2 = '1';
''')

        self.__AfterPull__ ='''
    if( self.rx.ready = '1'  and self.rx.valid ='1') then 
        self.data_isvalid := '1';
    end if;

    self.data_internal_was_read2 := '0';
    self.rx.ready := '0';


    if (self.data_isvalid ='1' and  self.data_internal_isvalid2 = '0') then
        self.data_internal2:= self.rx.data ;
        self.data_internal_isvalid2 := self.data_isvalid;
        self.data_internal_isLast2 := self.rx.last;
        self.data_isvalid:='0';

    end if;
        '''

        self.__BeforePush__='''
    if (self.data_internal_was_read2 = '1'   ) then
      self.data_internal_isvalid2 := '0';
    end if;


    if (self.data_isvalid = '0'   and self.data_internal_isvalid2 = '0' ) then 
        self.rx.ready := '1';
    end if;
        '''


class axisStream_master(v_class):
    def __init__(self, AXiName,AxiType):
        super().__init__("axisStream_"+ str(AXiName)+"_master")
        self.tx = port_Master(axisStream(AXiName,AxiType))
        self.__v_classType__         = v_classType_t.Master_t
        self.__vectorPull__ = True
        self.__vectorPush__ = True
        
        self.send_data = v_procedure(argumentList= "datain : in " + self.tx.data.type, body='''
   self.tx.valid   := '1';
   self.tx.data    := datain; 
''')
        
        self.ready_to_send = v_function(returnType="boolean",body = '''
    return self.tx.valid = '0';
''')
        self.Send_end_Of_Stream = v_procedure(argumentList= "EndOfStream : in boolean := true",body='''
    if EndOfStream then 
        self.tx.last := '1';
    else 
        self.tx.last := '0';
    end if; 
''')

        self.__AfterPull__ ='''
    if (self.tx.ready = '1') then 
        self.tx.valid   := '0'; 
        self.tx.last := '0';  
        self.tx.data := {default};
    end if;
        '''.format(
            default=AxiType.DefaultValue
        )

class axisStream_master_with_strean_counter(v_class):
    def __init__(self, AXiName, AxiType):
        super().__init__("axisStream_"+ str(AXiName)+"_master_with_counter")
        self.AxiTX = port_Master(axisStream_master(AXiName,AxiType))
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

def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_axiStream_zerosupression.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_axiStream_zerosupression")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    AXiName,AxiType = arg2type(sp[2])


    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
        axisStream(AXiName,AxiType),
        axisStream_slave(AXiName,AxiType),
        axisStream_master(AXiName,AxiType),
        axisStream_master_with_strean_counter(AXiName,AxiType)
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)



if __name__== "__main__":
    main()

