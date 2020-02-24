

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

tb.hdl_conversion__.convert_all(tb,"test_fifo")


