import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *
from CodeGen.xgenDB import *


class counter(v_class):
    def __init__(self, CounterLength):
        super().__init__("counter_"+ str(CounterLength))
        self.__v_classType__         = v_classType_t.Slave_t
        
        self.Running = v_sl()
        self.Count = v_slv(CounterLength)
        self.MaxCount = v_slv(CounterLength)

    def _onPull(self):
        if self.Running:
            self.Count <<  self.Count +1

        if self.Count >= self.MaxCount:
            self.Running << 0
            self.Count << 0
    

    def StartCountTo(self, MaxCount= port_in(v_slv())):
        if not self.Running:
            self.Running<<1
            self.MaxCount << MaxCount
            self.Count << 0

    def stopCounter(self):
        self.Running << 0

    def isRunning(self):
        return self.Running == 1


    def InTimeWindowSLV(self,TimeMin=port_in(v_slv()),TimeMax=port_in(v_slv()), DataIn=port_in(v_slv())):
        
        DataOut=v_slv("DataIn'length")
        DataOut << 0
        if self.Running and TimeMin <= self.Count and self.Count < TimeMax:
            DataOut << DataIn

        return DataOut

    def InTimeWindowSl(self,TimeMin=port_in(v_slv()),TimeMax=port_in(v_slv())):
        DataOut=v_sl()
        DataOut << 0
        if self.Running and TimeMin <= self.Count and self.Count < TimeMax:
            DataOut << 1  
        return DataOut
        
def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_Counter.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_Counter")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
      counter(16)
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
