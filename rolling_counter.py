import argparse
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *

from enum import Enum 
import copy 


class rollingCounter(v_class):
    def __init__(self):
        super().__init__("rollingCounter")
        self.__v_classType__         = v_classType_t.Slave_t
        self.Counter = v_int()
       
    def reset(self):
        self.Counter << 0
        
    def incr(self,MaxCount=port_in(v_int())):
        self.Counter << self.Counter + 1
        if self.Counter ==MaxCount:
            self.Counter << 0 


        
def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_rollingCounter.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_rollingCounter")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
      rollingCounter()
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
