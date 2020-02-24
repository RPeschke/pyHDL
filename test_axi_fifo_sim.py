

import unittest
import functools
import argparse
import os,sys,inspect
import copy
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import CodeGen.axi_fifo 
from CodeGen.xgenPackage import *



tb = CodeGen.axi_fifo.test_bench_e123()

CodeGen.axi_fifo.gsimulation.run_timed(tb, 1000,"axi_fifo.vcd")