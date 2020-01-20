import argparse
import os,sys,inspect
import copy
from enum import Enum 

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *
from CodeGen.xgenDB import *


class counter_state(Enum):
    idle    = 0
    running = 1
    done    = 2

class time_span(v_class):
    def __init__(self, CounterLength):
        super().__init__("time_span"+ str(CounterLength))
        self.__v_classType__         = v_classType_t.Record_t
        self.min  = v_slv(CounterLength)
        self.max  = v_slv(CounterLength)

class counter(v_class):
    def __init__(self, CounterLength):
        super().__init__("counter_"+ str(CounterLength))
        self.__v_classType__         = v_classType_t.Slave_t
        AddDataType(  time_span(CounterLength)  )
        self.state = v_enum(counter_state)
        self.Count = v_slv(CounterLength)
        self.MaxCount = v_slv(CounterLength)

    def _onPull(self):
        if self.isRunning():
            self.Count <<  self.Count +1

        if self.isRunning() and self.Count >= self.MaxCount:
            self.state << counter_state.done
            self.Count << 0

    

    def StartCountTo(self, MaxCount= port_in(v_slv())):
        if self.isReady():
            self.state << counter_state.running
            self.MaxCount << MaxCount
            self.Count << 0
            

    def StartCountFromTo(self,MinCount= port_in(v_slv()), MaxCount= port_in(v_slv())):
        if self.isReady():
            self.state << counter_state.running
            self.MaxCount << MaxCount
            self.Count << MinCount


        
    def stopCounter(self):
        self.state << counter_state.done
    
    def isReady(self):
        return self.state == counter_state.idle

    def isRunning(self):
        return self.state == counter_state.running
    
    def isDone(self):
        return self.state == counter_state.done

    def reset(self):
        self.state << counter_state.idle
        self.Count << 0



    def InTimeWindowSLV(self,TimeMin=port_in(v_slv()),TimeMax=port_in(v_slv()), DataIn=port_in(v_slv())):
        
        DataOut=v_slv("DataIn'length")
        DataOut << 0
        if self.isRunning() and TimeMin <= self.Count and self.Count < TimeMax:
            DataOut << DataIn

        return DataOut

    def InTimeWindowSl(self,TimeMin=port_in(v_slv()),TimeMax=port_in(v_slv())):
        DataOut=v_sl()
        DataOut << 0
        if self.isRunning() and TimeMin <= self.Count and self.Count < TimeMax:
            DataOut << 1  
        return DataOut
        

    def InTimeWindowSLV_r(self,TimeSpan=port_in(dataType()), DataIn=port_in(v_slv())):
        
        DataOut=v_slv("DataIn'length")
        DataOut << 0
        if self.isRunning() and TimeSpan.min <= self.Count and self.Count < TimeSpan.max:
            DataOut << DataIn

        return DataOut

    def InTimeWindowSl_r(self,TimeSpan=port_in(dataType())):
        DataOut=v_sl()
        DataOut << 0
        if self.isRunning() and TimeSpan.min <= self.Count and self.Count < TimeSpan.max:
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
      v_enum ( counter_state),        
      time_span(16),
      counter(16)
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
