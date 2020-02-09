

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


#ax = CodeGen.example4.tb_entity()
#vhdl = ax.hdl_conversion__.get_entity_definition(ax)
#file_set_content("CodeGen/tests/example1_new.vhd",vhdl)
#vhdl_ref = file_get_contents("CodeGen/tests/example1.vhd")
#print(vhdl == vhdl_ref)
#print(vhdl)

ax = v_package("CodeGen_example4_tb_entity",sourceFile=__file__,
    PackageContent = [
        CodeGen.example4.axiFilter(),
        CodeGen.example4.axiPrint(),
        CodeGen.example4.clk_generator(),
        CodeGen.example4.rollingCounter(),
        CodeGen.example4.tb_entity()
    ]
    )
fileContent = ax.to_string()
print(fileContent)
