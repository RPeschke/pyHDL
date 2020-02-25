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



class rollingCounter(v_clk_entity):
    def __init__(self,clk=None,MaxCount=v_slv(32,100)):
        super().__init__(__file__, clk)
        self.Axi_out = port_Stream_Master( axisStream(v_slv(32)))
        self.MaxCount = port_in(v_slv(32,10))
        self.MaxCount << MaxCount
        self.architecture()
    
    def architecture(self):
        
        counter = v_slv(32)
        v_Axi_out = get_master(self.Axi_out)
        @rising_edge(self.clk)
        def proc():
            if v_Axi_out:
                v_Axi_out << counter
                
                counter << counter + 1

            if counter > self.MaxCount:
                counter << 0