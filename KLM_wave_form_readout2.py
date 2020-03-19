
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

from CodeGen.axi_stream_delay import *


from CodeGen.xgen_simulation import *
from CodeGen.clk_generator import *



class SerialDataConfig(v_class):
    def __init__(self):
        super().__init__("SerialDataConfig")
        self.__v_classType__       = v_classType_t.Record_t

        self.row_Select            =  v_slv(3)
        self.column_select         =  v_slv(6)
        self.ASIC_NUM              =  v_slv(5)
        self.force_test_pattern    =  v_sl() 
        self.sample_start          =  v_slv(5)
        self.sample_stop           =  v_slv(5)


class register_t(v_class):
    def __init__(self):
        super().__init__("register_t")
        self.__v_classType__       = v_classType_t.Record_t
        self.address   = v_slv(16) 
        self.value     = v_slv(16) 
        


class klm_globals(v_class):
    def __init__(self):
        super().__init__("klm_globals")
        self.__v_classType__       = v_classType_t.Record_t
        self.clk   =  v_sl() 
        self.rst   =  v_sl() 
        self.reg   =  register_t() 

class InputDelay(v_entity):
    def __init__(self,k_globals =None,InputType = v_slv(32),Delay=0):
        super().__init__(__file__)
        self.globals  = port_Slave(klm_globals())
        if k_globals != None:
            self.globals  << k_globals
        self.ConfigIn = port_Stream_Slave(axisStream( InputType))
        self.ConfigOut = port_Stream_Master(axisStream( InputType))
        self.Delay = Delay
        self.architecture()

    @architecture
    def architecture(self):
        
#        pipe = self.ConfigIn \
#            | stream_delay_one(self.globals.clk, self.ConfigIn.data) \
#            | stream_delay_one(self.globals.clk, self.ConfigIn.data) \
#            | stream_delay_one(self.globals.clk, self.ConfigIn.data) \
#            | \
#        self.ConfigOut   
        pipe2 = delay(times=self.Delay,obj=self)
        end_architecture()


def delay(times,obj):
    pipe1 = obj.ConfigIn |  stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
    for x in range(times):
        pipe1 |   stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
            

    pipe1 |   obj.ConfigOut
    return pipe1

class InputDelay_print(v_entity):
    def __init__(self,k_globals =None,InputType =v_slv(32)):
        super().__init__(__file__)
        self.globals  = port_Slave(klm_globals())
        if k_globals != None:
            self.globals << k_globals
        self.ConfigIn = port_Stream_Slave(axisStream( InputType))
        self.architecture()

    @architecture
    def architecture(self):
        d =  v_copy(self.ConfigIn.data)
        ax_slave = get_salve(self.ConfigIn)
        @rising_edge(self.globals.clk)
        def proc():
            if ax_slave:
               d << ax_slave
               print(value(d.column_select))


        end_architecture()

class InputDelay_tb(v_entity):
    def __init__(self):
        super().__init__(srcFileName=__file__)
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        k_globals =klm_globals()
        data = v_slv(32)
        dut  = v_create(InputDelay(k_globals,Delay=5) )

        axprint  =  v_create( InputDelay_print(k_globals))

        axprint.ConfigIn << dut.ConfigOut
        k_globals.clk << clkgen.clk
        mast = get_master(dut.ConfigIn)


        @rising_edge(clkgen.clk)
        def proc():
            if mast:
                mast << data
                data << data + 1

        end_architecture()



import cProfile, pstats, io



def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

#@profile
def main():
    tb  =v_create(InputDelay_tb())
    #gsimulation.run_timed(tb, 1000,"InputDelay_tb.vcd")
    tb.hdl_conversion__.convert_all(tb,"pyhdl_waveform")

main()