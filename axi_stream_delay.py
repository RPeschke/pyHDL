
import unittest
import functools
import argparse
import os,sys,inspect
import copy

from .xgenBase import *
from .xgen_v_symbol import *
from .axiStream import *
from .xgen_v_entity import *
from .xgen_v_list import *
from .xgen_simulation import *


class stream_delay_one(v_clk_entity):
    def __init__(self,clk=None,itype =v_slv(32)):
        super().__init__(__file__, clk)
        self.Axi_in = port_Stream_Slave(axisStream(itype))
        self.Axi_out = port_Stream_Master(axisStream(itype))
        self.architecture()

        
    def architecture(self):
        axiSalve = get_salve(self.Axi_in)
        axMaster = get_master(self.Axi_out) 
        @rising_edge(self.clk)
        def proc():
            if axiSalve and axMaster:
                axMaster << axiSalve

        end_architecture()


class stream_delay(v_clk_entity):
    def __init__(self,clk=None,itype =v_slv(32),depth=10):
        super().__init__(__file__, clk)
        self.Axi_in = port_Stream_Slave(axisStream(itype))
        self.Axi_out = port_Stream_Master(axisStream(itype))
        self.depth = v_const(v_int(depth))
        self.array_size  = v_const(v_int(2**value(depth) ))
        self.architecture()



    def architecture(self):
        
        pipe1 = self.Axi_in \
            |  stream_delay_one(self.clk,  self.Axi_in.data) \
            |   stream_delay_one(self.clk, self.Axi_in.data) \
            |   stream_delay_one(self.clk, self.Axi_in.data) \
            |   stream_delay_one(self.clk, self.Axi_in.data) \
            | \
        self.Axi_out

        end_architecture()

