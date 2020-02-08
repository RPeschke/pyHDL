
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

from CodeGen.klm_scrod_bus import *
from CodeGen.serialdatarout import *

class klm_globals(v_class):
    def __init__(self):
        super().__init__("klm_globals")
        self.clk   = port_out( v_sl() )
        self.rst   = port_out( v_sl() )
        self.reg   = port_out( v_slv(32) )
        

class InputDelay(v_clk_entity):
    def __int__(self,k_globals =klm_globals()):
        super().__init__(__file__, k_globals.clk)
        self.globals  = port_in(k_globals)
        InputType = SerialDataConfig()
        self.ConfigIn = port_Stream_Slave(axisStream( type(InputType).__name__ ,InputType))
        self.ConfigOut = port_Stream_Master(axisStream( type(InputType).__name__ ,InputType))
    
    def architecture(self):
        self.ConfigIn \
            | serialize(self.globals,axisStream("32",v_slv(32))) \
            | axiStreamDelayBuffer(self.globals) \
            | ax_fifo(self.globals)  \
            | deserialize(self.globals) \
            | \
        self.ConfigOut   

        end_architecture()
        


class TXWaveFormReadout(v_clk_entity):
    def __init__(self,k_globals =klm_globals()):
       super().__init__(__file__, k_globals.clk)
       InputType = SerialDataConfig()
       self.globals  = port_in(k_globals)
       self.ConfigIn = port_Stream_Slave(axisStream( type(InputType).__name__ ,InputType))
       self.TX_Bus   = port_Slave(DataBus())
       self.TX_stream_data = port_out(v_slv(16))
       self.Data_out  = port_Stream_Master(axisStream("32",v_slv(32)))
       self.architecture()

    def architecture(self):


        splitter = axi_splitter(self.globals)
        data_pipe = \
            self.ConfigIn \
                | InputDelay(self.globals) \
                | splitter(0, 0)
                | TX_write_handler(self.globals,self.TX_Bus.WriteSignals) \
                | TX_WillkonsonControl(self.globals,self.TX_Bus.SamplingSignals) \
                | SerialDataRoutProcess_cl(self.globals,self.TX_Bus.ShiftRegister)\
                | SerialOutputCOnverter(self.globals) \
                | pedestal_Substraction(self.globals, splitter(1))
                | ax_fifo(self.globals) \
                | \
            self.Data_out



        end_architecture()

