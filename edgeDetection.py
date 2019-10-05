import argparse
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *

from enum import Enum 
import copy 


class edgeDetection(v_class):
    def __init__(self):
        super().__init__("edgeDetection")
        self.rx = port_in (v_sl())
        self.__v_classType__         = v_classType_t.Slave_t
       
        self.oldRX =v_sl()
        self.oldRX1 =v_sl()

    def _onPull(self):
        self.oldRX1 << self.oldRX
        self.oldRX << self.rx
    
    def rising_edge(self):
        return not self.oldRX1 and self.oldRX

    def falling_edge(self):
        return  self.oldRX1 and not self.oldRX

        
def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_edgeDetection.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_edgeDetection")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
      edgeDetection()
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
