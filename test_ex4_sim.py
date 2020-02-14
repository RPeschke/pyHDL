

import unittest
import functools
import argparse
import os,sys,inspect
import copy
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import CodeGen.Example1 
import CodeGen.example2 
import CodeGen.example3 
import CodeGen.example4 
from CodeGen.xgenPackage import *

def file_set_content(filename,content):
    with open(filename,'w') as f:
        f.write(content)

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()

ax = CodeGen.example4.tb_entity()
CodeGen.example4.gsimulation.run_timed(ax, 1000,"example4.vcd")