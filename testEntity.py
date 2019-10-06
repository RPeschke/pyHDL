
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

def test():
    print("SDAads")
class axiFifo(v_entity):
    def __init__(self):
        super().__init__("axiFifo",__file__)
        self.clk    = port_in(v_sl())
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))

        self.i_buff = v_slv(32,123)

    def _process1(self):
        axiSalve = axisStream_slave(32,v_slv(32))
        axiSalve.Connect(self.Axi_in )

        #@rising_edge(self.clk)
        def _proc():
            if axiSalve:
                axiSalve << 123
        
        proc = _proc
        return proc
        

ax = axiFifo()
print(ax.get_definition())