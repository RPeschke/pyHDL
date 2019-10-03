import argparse
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *

from enum import Enum 

class clk_domain_crossing(v_class):
    def __init__(self):
        super().__init__("clk_domain_crossing")


        self.isValid               = port_out( v_sl() )  
        self.isDone                = port_in( v_sl() )  
        self.DoneReceived          = port_out( v_sl() )  
        self.data                  = port_out(v_slv(32))

class clk_domain_crossing_master(v_class):
    def __init__(self):
        super().__init__("clk_domain_crossing_master")
        self.__v_classType__    = v_classType_t.Master_t
        self.tx                 = port_Master(clk_domain_crossing())
    
    def _onPull(self):
        if self.tx.isDone:
            self.tx.DoneReceived << '1'

        if self.tx.DoneReceived and not self.tx.isDone:
            self.tx.DoneReceived << 0
            self.tx.isValid << 0
  
    def isReady(self):
        return self.tx.isValid == False


    def sendData(self,data = port_in(v_slv(32))):
        if self.isReady():
            self.tx.isValid << 1
            self.tx.data << data
        

class clk_domain_crossing_slave(v_class):
    def __init__(self):
        super().__init__("clk_domain_crossing_slave")
        self.__v_classType__    = v_classType_t.Slave_t
        self.rx = port_Slave(clk_domain_crossing())

    def _onPull(self):
        if self.rx.DoneReceived:
            self.rx.isDone << 0
              
              
    def isReady(self):
        return self.rx.isValid  and  not self.rx.isDone and not self.rx.DoneReceived


    def ReadData(self, DataOut =port_out( v_slv(32))):
        test = v_slv(12)
        self.rx.isDone << 1
        DataOut << self.rx.data
        test << 2
        



def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_clk_domain_crossing.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="clk_domain_crossing")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    pac = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
        clk_domain_crossing(),
        clk_domain_crossing_master(),
        clk_domain_crossing_slave()
    ]
    
    
    )
    xgenAST1 = xgenAST(__file__)
    fun= list(xgenAST1.extractFunctionsForClass(clk_domain_crossing_master() ,pac ))
#print(fun)
    for f in fun:
        print(f.getHeader("",None))
        print(f.getBody("",None))
    fileContent = pac.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
