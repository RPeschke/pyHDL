
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
        self.Axi_in\
            |  stream_delay_one(self.clk) \
            |   \
        self.Axi_out

        end_architecture()

class test_bench_stream_delay(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()

    def architecture(self):
        clkgen = v_create(clk_generator())
        maxCount = v_slv(32,20)
        pipe1 = rollingCounter(clkgen.clk,maxCount) \
            | stream_delay(clkgen.clk)  \
            | axiPrint(clkgen.clk) 
        
        end_architecture()