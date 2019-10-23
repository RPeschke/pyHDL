
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





class axiFifo(v_entity):
    def __init__(self):
        super().__init__("axiFifo",__file__)
        self.clk    =  port_in(v_sl())
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))
        self.Axi_out = port_Master(axisStream(32,v_slv(32)))

        self.i_buff = v_slv(32,123,varSigConst=varSig.signal_t)



    def _process1(self):
        axiSalve = axisStream_slave(self.Axi_in)
        axiMaster = axisStream_master(self.Axi_out)

        @rising_edge(self.clk)
        def proc():
            if axiSalve:
                self.i_buff << axiSalve

            if axiMaster:
                axiMaster << self.i_buff


        return proc
        

ax = axiFifo()


b = ax()


print(ax._get_definition())