
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


class clk_generator(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.clk = port_out(v_sl())
        self.architecture()

    def architecture(self):
        
        @timed()
        def proc():
            self.clk << 1
            #print("======================")
            yield wait_for(1)
            self.clk << 0
            yield wait_for(1)


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


class axiFifo(v_clk_entity):
    def __init__(self,clk=None,itype =v_slv(32),depth=10):
        super().__init__(__file__, clk)
        self.Axi_in = port_Stream_Slave(axisStream(itype))
        self.Axi_out = port_Stream_Master(axisStream(itype))
        self.depth = v_const(v_int(depth))
        self.array_size  = v_const(v_int(2**value(depth) ))
        self.architecture(itype,depth)

        
    def architecture(self,itype,depth):
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

            if  not i_valid and counter > 0:
                counter    << counter - 1
                i_valid << 1


            if tail_index == len(sList) - 1:
                tail_index << 0
        
            self.Axi_out.valid << i_valid 

        end_architecture()
class test_bench_e123(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()

    def architecture(self):
        clkgen = v_create(clk_generator())
        maxCount = v_slv(32,20)
        axigen =   v_create(rollingCounter(clkgen.clk,maxCount))
        axp    =  v_create(axiPrint(clkgen.clk))
        fifo   =  v_create(axiFifo(clkgen.clk))
        fifo.Axi_in << axigen.Axi_out
        axp.Axi_in << fifo.Axi_out