
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

        s_buff = v_signal( v_slv(32) )
        s_buff2 = v_signal( v_slv(32) )
        s_sw    = v_signal( v_sl() )
        @combinational() 
        def p1():
            s_buff << self.Axi_in.data    
            s_buff2 << v_switch( 0 , [
                v_case(  self.Axi_in.data < 5 , self.Axi_in.data)
                ]  )


        axiSalve = axisStream_slave(self.Axi_in)
        axMaster = axisStream_master(self.Axi_out) 


        i_buff = v_variable( v_slv(32) )
        @rising_edge(self.clk)
        def proc():
        #print("axiPrint",value(  i_buff) )
            s_sw << 0
            if axiSalve and axMaster:
                i_buff << axiSalve
                if i_buff < 10:
                    axMaster << axiSalve
                    s_sw << 1
                    #print("axiPrint valid",value( i_buff) )
        
        
        end_architecture()


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
                #print("axiPrint",value(i_buff) )
                if axiSalve :
                    i_buff << axiSalve
                    #print("axiPrint valid",value(i_buff) )



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
                #print("======================")
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
                    #print("counter", value( counter) )
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

        
        pipe1  = rollingCounter(clkgen.clk,maxCount)  \
                    | axiFilter(clkgen.clk) \
                    | axiPrint(clkgen.clk)
        
        end_architecture()


                





#ax = tb_entity()
#gsimulation.run_timed(ax, 1000,"example4.vcd")

#print(ax._get_definition())