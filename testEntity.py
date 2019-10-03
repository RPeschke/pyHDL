
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

class axiFifo(v_entity):
    def __init__(self):
        super().__init__("axiFifo")
        self.clk    = port_in(v_sl())
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))

        self.i_buff = v_slv(32,123)
        

ax = axiFifo()
print(ax.get_definition())