
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





class axiFifo(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)

           
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))
        self.Axi_out = port_Master(axisStream(32,v_slv(32)))

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
    
    def architecture(self):
        clk = v_sl(varSigConst=varSig.signal_t)
        ax1 = v_create( axiFifo(clk))
        ax2 = v_create( axiFifo(clk))


        ax2.Axi_in << ax1.Axi_out         


ax = tb_entity()





print(ax._get_definition())

axB= axiFifo()

#print(axB._get_definition())