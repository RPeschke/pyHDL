
import functools
import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from CodeGen.xgenBase import *
from CodeGen.xgen_v_symbol import *
from CodeGen.axiStream import *
from CodeGen.xgen_v_entity import *


from CodeGen.xgen_simulation import *




class SerialDataConfig(v_class):
    def __init__(self):
        super().__init__("SerialDataConfig")
        self.__v_classType__       = v_classType_t.Record_t

        self.row_Select            =  v_slv(3)
        self.column_select         =  v_slv(6)
        self.ASIC_NUM              =  v_slv(5)
        self.force_test_pattern    =  v_sl() 
        self.sample_start          =  v_slv(5)
        self.sample_stop           =  v_slv(5)


class register_t(v_class):
    def __init__(self):
        super().__init__("register_t")
        self.__v_classType__       = v_classType_t.Record_t
        self.address   = v_slv(16) 
        self.value     = v_slv(16) 
        


class klm_globals(v_class):
    def __init__(self):
        super().__init__("klm_globals")
        self.clk   = port_out( v_sl() )
        self.rst   = port_out( v_sl() )
        self.reg   = port_out(register_t() )

class InputDelay(v_clk_entity):
    def __init__(self,k_globals =klm_globals()):
        print("Sdasdas")
        super().__init__(__file__, k_globals.clk)
        self.globals  = port_Slave(k_globals)
        InputType = SerialDataConfig()
        self.ConfigIn = port_Stream_Slave(axisStream( InputType))
        self.ConfigOut = port_Stream_Master(axisStream( InputType))
        #self.architecture()



def main():
    tb  =v_create(InputDelay())

    tb.hdl_conversion__.convert_all(tb,"pyhdl_waveform")

main()