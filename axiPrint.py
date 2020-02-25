
import unittest
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
from CodeGen.xgen_v_list import *

from CodeGen.xgen_simulation import *


class axiPrint(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)
        self.Axi_in =  port_Stream_Slave(axisStream(v_slv(32)))
        self.architecture()

        
    def architecture(self):
        axiSalve =  get_salve(self.Axi_in)

        i_buff = v_slv(32)

        @rising_edge(self.clk)
        def proc():
            
            if axiSalve :
                i_buff << axiSalve
                print("axiPrint valid",value(i_buff) )