
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




class axiFilter(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)
        self.Axi_in = port_Stream_Slave(axisStream(32,v_slv(32)))
        self.Axi_out = port_Stream_Master(axisStream(32,v_slv(32)))
        self.architecture()

        
    def architecture(self):
        @process()
        def _process1():
            axiSalve = axisStream_slave(self.Axi_in)
            axMaster = axisStream_master(self.Axi_out) 


            i_buff = v_slv(32)
            @rising_edge(self.clk)
            def proc():
                print("axiPrint",i_buff.value )
                if axiSalve and axMaster:
                    i_buff << axiSalve
                    if i_buff < 10:
                        axMaster << axiSalve
                        print("axiPrint valid",i_buff.value )

class axiPrint(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)
        self.Axi_in =  port_Stream_Slave(axisStream(32,v_slv(32)))
        self.architecture()

        
    def architecture(self):
        @process()
        def _process1():
            axiSalve = axisStream_slave(self.Axi_in)

            i_buff = v_slv(32)

            @rising_edge(self.clk)
            def proc():
                print("axiPrint",i_buff.value )
                if axiSalve :
                    i_buff << axiSalve
                    print("axiPrint valid",i_buff.value )



class clk_generator(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.clk = port_out(v_sl())
        self.architecture()

    def architecture(self):
        
        @process()
        def p1():

            @timed()
            def proc():
                self.clk << 1
                print("======================")
                yield wait_for(10)
                self.clk << 0
                yield wait_for(10)


class rollingCounter(v_clk_entity):
    def __init__(self,clk=None,MaxCount=v_slv(32,100)):
        super().__init__(__file__, clk)
        self.Axi_out = port_Stream_Master( axisStream(32,v_slv(32)))
        self.MaxCount = port_in(v_slv(32,10))
        self.MaxCount << MaxCount
        self.architecture()
    
    def architecture(self):
        
        counter = v_slv(32)
        @process()
        def p2():
            v_Axi_out = axisStream_master(self.Axi_out)
            @rising_edge(self.clk)
            def proc():
                if v_Axi_out:
                    print("counter", counter.value)
                    v_Axi_out << counter
                
                    counter << counter + 1

                if counter > self.MaxCount:
                    counter << 0


class tb_entity(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()
        


    def architecture(self):
        clkgen = v_create(clk_generator())

        maxCount = v_slv(32,20)
        axiSource = v_create(rollingCounter(clkgen.clk,maxCount))
        axP       = v_create(axiPrint(clkgen.clk))
        axFilter  = v_create(axiFilter(clkgen.clk))
        
        axiSource | axFilter | axP
        
        end_architecture()


                





ax = tb_entity()
gsimulation.run_timed(ax, 1000,"example3.vcd")

print(ax._get_definition())