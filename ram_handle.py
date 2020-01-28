import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *
from CodeGen.xgenDB import *


class ram_handle(v_class):
    def __init__(self,ram_handle_name,AddressLength, ram_handle_type):
        super().__init__("ram_handle"+str(ram_handle_type))
        AddDataType(  ram_handle_type  )
        self.writeEnable    = port_out( v_sl() )
        self.writeAddress   = port_out( v_slv(AddressLength) )
        self.writeData      = port_out( ram_handle_type  )
        self.readAddress    = port_out( v_slv(AddressLength) )
        self.readData       = port_in( ram_handle_type  )
        

class ram_handle_master(v_class):
    def __init__(self, ram_handle):
        super().__init__(ram_handle.type + "_master")
        self.__v_classType__         = v_classType_t.Master_t
        self.txrx = port_Master(ram_handle)
        self.writeEnable_internal  =  v_sl()
        self.requesting_data       =  v_sl()
        self.readAddress0          =  v_copy(ram_handle.readAddress)
        self.readData0             =  v_copy(ram_handle.readData)
        self.readData0_was_read    =  v_sl()
        self.readAddress1          =  v_copy(ram_handle.readAddress)
        self.readData1             =  v_copy(ram_handle.readData)  
        self.readData1_was_read    =  v_sl()
        
    def _onPull(self):

        if self.requesting_data :
            self.readData1      << self.readData0
            self.readAddress1   << self.readAddress0
            self.readData0      << self.txrx.readData
            self.readAddress0   << self.txrx.readAddress

        self.writeEnable_internal  <<  0
        self.requesting_data       <<  0
        self.readData1_was_read    <<  0
        self.readData0_was_read    <<  0

    def _onPush(self):
        if not self.requesting_data and self.readData0_was_read:
            self.txrx.readAddress << self.readAddress0 +1
            self.requesting_data << 1


    def isReady2Store(self):
        return self.writeEnable_internal == 0

    def Store_Data(self,Address = port_in( v_slv() ),Data = port_in( dataType()  )):
        if self.isReady2Store():
            self.writeEnable_internal << 1
            self.txrx.writeAddress << Address
            self.txrx.writeData  << Data

    
    def request_Data(self,Address = port_in(v_slv())):
                 
        if self.requesting_data == 0 and not (self.readAddress0 == Address or self.readAddress1 == Address):
            self.txrx.readAddress << Address
            self.requesting_data  << 1

    def isReady2Load(self, Address = port_in(v_slv())):
        return self.readAddress0 == Address or self.readAddress1 == Address
            

    def read_Data(self,  Address = port_in(v_slv()), Data = port_out( dataType()  )):
        if self.readAddress0 == Address:
            Data << self.readData0
            self.readData0_was_read  << 1
        elif self.readAddress1 == Address:
            Data << self.readData1
            self.readData0_was_read << 1


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
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_ramHandler_32_5.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_ramHandler_32_5")
    s = isConverting2VHDL()
    set_isConverting2VHDL(True)
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    AXiName, AxiType = arg2type(sp[2])

    ax_t = ram_handle(AXiName,int(sp[3]), AxiType)
    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
        ax_t,
        ram_handle_master(ax_t)
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)
        
    set_isConverting2VHDL(s)


if __name__== "__main__":
    main()
