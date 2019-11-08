

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


class tb_entity(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()


    def architecture(self):
        clk = v_sl()


        @process()
        def p1():

            @timed()
            def proc():
                clk << 1
                print("set clk to 1")
                yield wait_for(10)
                clk << 1
                #print("set clk to 1 again")
                yield wait_for(10)
                clk << 0
                #print("set clk to 0")
                yield wait_for(10)

        counter = v_slv(32)
        @process()
        def p2():
            v_counter = v_slv(32)
            @rising_edge(clk)
            def proc():
                v_counter << v_counter +1
                counter << counter + 1
                print("counter", counter.value)
                print("v_counter", v_counter.value)


ax = tb_entity()
gsimulation.run_timed(ax, 1000,"example1.vcd")
print("===== end of Simulation =============")
print(ax._get_definition())
