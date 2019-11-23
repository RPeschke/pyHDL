import argparse
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *


class TX_DAC_control(v_class):
    def __init__(self):
        super().__init__("TX_DAC_control")
        self.SIN     = port_out(v_sl())
        self.SCLK    = port_out(v_sl())
        self.PCLK    = port_out(v_sl())
        self.REG_CLR = port_out(v_sl())


class TXWriteSignals(v_class):
    def __init__(self):
        super().__init__("TXWriteSignals")
        self.writeEnable_1 = port_in(v_slv(5))
        self.writeEnable_2 = port_in(v_slv(5))
        self.clear         = port_in(v_sl())
        

class TXSamplingSignals(v_class):
    def __init__(self):
        super().__init__("TXSamplingSignals")
        self.read_row_select_s    = port_in(  v_slv(3)) 
        self.read_column_select_s = port_in(  v_slv(6))    
        self.clr                  = port_in(  v_sl())
        self.ramp                 = port_in(  v_sl())
        self.read_enable          = port_in(  v_sl())


        
class TXShiftRegisterSignals(v_class):
    def __init__(self):
        super().__init__("TXShiftRegisterSignals")
        self.data_out         = port_out( v_slv(16) )  # one bit per Channel
        
        #sr = Shift Register 
        self.sr_clear         = port_in( v_sl() )
        self.sr_Clock         = port_in( v_slv(5) )
        self.sr_select        = port_in( v_sl() )

        self.SampleSelect     = port_in( v_slv(5) )
        self.SampleSelectAny  = port_in( v_slv(5) )

class DataBus(v_class):
    def __init__(self):
        super().__init__("DataBus")
        self.WriteSignals    = port_Master(TXWriteSignals())
        self.SamplingSignals = port_Master(TXSamplingSignals())
        self.ShiftRegister   = port_Master(TXShiftRegisterSignals())


      
def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/xgen_klm_scrod_bus.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="xgen_klm_scrod_bus")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    ax = v_package(args.PackageName,sourceFile=__file__,
    PackageContent = [
        TXSamplingSignals(),
        TXWriteSignals(),
        TXShiftRegisterSignals(),
        DataBus(),
        TX_DAC_control()
    ]
    
    
    )
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)




if __name__== "__main__":
    main()
