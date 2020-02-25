
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


class axiFifo(v_clk_entity):
    def __init__(self,clk=None,itype =v_slv(32),depth=10):
        super().__init__(__file__, clk)
        self.Axi_in = port_Stream_Slave(axisStream(itype))
        self.Axi_out = port_Stream_Master(axisStream(itype))
        self.depth = v_const(v_int(depth))
        self.array_size  = v_const(v_int(2**value(depth) ))
        self.architecture()

        
    def architecture(self):
        axiSalve = get_salve(self.Axi_in)
        #axMaster = get_master(self.Axi_out) 
        sList = v_list(v_copy(self.Axi_in.data), self.array_size)

        head_index = v_slv( value( self.depth)+1)
        tail_index =v_slv(value(self.depth)+1)
        counter = v_variable(v_slv(value(self.depth)+1))
        i_valid = v_variable(v_sl())

        @combinational()
        def p2():
            self.Axi_out.data << sList[tail_index]
            


        @rising_edge(self.clk)
        def proc():
        
            if axiSalve and counter < len(sList) :
                sList[head_index]  <<  axiSalve
                head_index << head_index + 1
                counter    << counter + 1
            
            if head_index == len(sList) - 1:
                head_index << 0

            if self.Axi_out.ready and i_valid:
                i_valid << 0
                tail_index << tail_index + 1
                counter    << counter - 1

            if  not i_valid and counter > 0:
                i_valid << 1


            if tail_index == len(sList) - 1:
                tail_index << 0
        
            self.Axi_out.valid << i_valid 

        end_architecture()