import argparse
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase import *
from CodeGen.xgenPackage import *

class B2TT(v_class):
    def __init__(self):
        super().__init__("B2TT")
        self.TTDACKP   = port_in( v_sl() )
        self.TTDACKN   = port_in( v_sl() )

        self.TTDTRGP   = port_in( v_sl() )
        self.TTDTRGN   = port_in( v_sl() )

        self.TTDCLKP   = port_out( v_sl() )
        self.TTDCLKN   = port_out( v_sl() )

        self.TTDRSVP   = port_out( v_sl() )
        self.TTDRSVP   = port_out( v_sl() )


class SFP(v_class):
    def __init__(self):
        super().__init__("SFP")
        
        self.MGTTXFAULT  = port_in( v_sl() )
        self.MGTMOD0     = port_in( v_sl() )
        self.MGTLOS      = port_in( v_sl() )
        
        self.MGTTXDIS   = port_out( v_sl() )
        self.MGTMOD2    = port_out( v_sl() )
        self.MGTMOD1    = port_out( v_sl() )

        self.mgtclk0p   = port_in( v_sl() )
        self.mgtclk0n   = port_in( v_sl() )


        self.mgtclk1p   = port_in( v_sl() )
        self.mgtclk1n   = port_in( v_sl() )


        self.mgtRXP   = port_in( v_sl() )
        self.mgtRXN   = port_in( v_sl() )

        self.mgtTXP   = port_out( v_sl() )
        self.mgtTXN   = port_out( v_sl() )


class DataBus(v_class):
    def __init__(self):
        super().__init__("DataBus")
        self.write_address_clock  = port_in(  v_sl())
        self.read_enable          = port_in(  v_sl())
        self.read_row_select_s    = port_in(  v_slv(3)) 
        self.read_column_select_s = port_in(  v_slv(6))
        self.clr                  = port_in(  v_sl())
        self.ramp                 = port_in(  v_sl())
        self.SAMPLESEL_S          = port_in(  v_slv(5))
        self.ShiftRegister_clear  = port_in(  v_sl())
        self.ShiftRegister_select = port_in(  v_sl())
        self.DataOut              = port_out( v_slv(16)) 


class DAC_Interface(v_class):
    def __init__(self):
        super().__init__("DAC_Interface")
        self.SIN   = port_out( v_sl())
        
        self.PCLK  = port_out( v_sl())
        self.SHOUT = port_in(  v_sl())
        self.SCLK  = port_out( v_sl())
        
#Digitization and sampling signals
class Digitization_and_sampling(v_class):
    def __init__(self):
        super().__init__("Digitization_and_sampling")
        self.WL_CLK_N    = port_out(v_sl())
        self.WL_CLK_P    = port_out(v_sl()) 
        self.WR1_ENA     = port_out(v_sl()) 
        self.WR2_ENA     = port_out(v_sl()) 
        self.SSTIN_N     = port_out(v_sl())
        self.SSTIN_P     = port_out(v_sl())		


class  klm_scrod_constrains_pkg(v_package):
    def __init__(self,PackageName):
        super().__init__(PackageName)
        self.B2TT = B2TT()
        self.SFP = SFP()
        self.DataBus =  DataBus()
        self.DAC_Interface =DAC_Interface()
        self.DAC_Interface_a = v_list( DAC_Interface(), 10)
        self.Digitization_and_sampling =Digitization_and_sampling()
        self.Digitization_and_sampling_a = v_list(Digitization_and_sampling, 10)



def main():
    
    parser = argparse.ArgumentParser(description='Generate Packages')
    parser.add_argument('--OutputPath',    help='Path to where the build system is located',default="build/xgen/klm_scrod_constrains_pkg.vhd")
    parser.add_argument('--PackageName',   help='package Name',default="klm_scrod_constrains_pkg")
   
    args = parser.parse_args()
    sp = args.PackageName.split("_")
    ax = klm_scrod_constrains_pkg(args.PackageName)
    fileContent = ax.to_string()
    with open(args.OutputPath, "w", newline="\n") as f:
        f.write(fileContent)



if __name__== "__main__":
    main()
