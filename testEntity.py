
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





class axiFifo(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)

           
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))
        self.Axi_out = port_Master(axisStream(32,v_slv(32)))
        self.architecture()

        
    def architecture(self):

        i_buff = v_slv(32,123,varSigConst=varSig.signal_t)


        @process()
        def _process1():
            axiSalve = axisStream_slave(self.Axi_in)
            axiMaster = axisStream_master(self.Axi_out)

            @rising_edge(self.clk)
            def proc():
                if axiSalve:
                    i_buff << axiSalve

                if axiMaster:
                    axiMaster << i_buff





class tb_entity(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()


    def architecture(self):
        clk = v_sl()
        ax1 = v_create( axiFifo(clk))
        ax2 = v_create( axiFifo(clk))


        ax2.Axi_in << ax1.Axi_out   
        clk2 = v_sl()
        clk2 << clk

        @process()
        def p1():

            @timed()
            def proc():
                clk << 1
                print("set clk to 1")
                yield wait_for(10)
                clk << 1
                print("set clk to 1 again")
                yield wait_for(10)
                clk << 0
                print("set clk to 0")
                yield wait_for(10)

        counter = v_slv(32)
        @process()
        def p2():
            
            @rising_edge(clk)
            def proc():
                counter << counter + 1
                print("p1", counter.value)
                


ax = tb_entity()


gsimulation.run_timed(ax, 1000,"test.vcd")

print(ax._get_definition())

axB= axiFifo()

#print(axB._get_definition())