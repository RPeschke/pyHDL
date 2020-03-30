
import unittest
import functools
import argparse
import os,sys,inspect
import copy

from .xgenBase import *
from .xgen_v_symbol import *
from .axiStream import *
from .xgen_v_entity import *
from .xgen_v_list import *

from .xgen_simulation import *


class clk_generator(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.clk = port_out(v_sl())
        self.architecture()
    
    @architecture
    def architecture(self):
        
        @timed()
        def proc():
            self.clk << 1
            print("======================")
            yield wait_for(10)
            self.clk << 0
            yield wait_for(10)

