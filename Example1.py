
import unittest
import functools
import argparse
import os,sys,inspect
import copy


from .xgenBase import *
from .xgen_v_symbol import *
from .axiStream import *
from .xgen_v_entity import *


from .xgen_simulation import *


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
                #print("set clk to 1")
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
                #print("counter", counter.value)
                #print("v_counter", v_counter.value)





