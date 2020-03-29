import sys
from vcd import VCDWriter
import  functools 
import inspect 


import os,sys,inspect
if __name__== "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from CodeGen.xgenBase import *
else:
    from .xgenBase import *


def getNameOf(obj):
    funcrec = inspect.stack()[2]

    f_locals = funcrec.frame.f_locals
    for y in f_locals:
        if obj is f_locals[y]:
            return y
    raise Exception("unable to find object")

class v_simulation():
    def __init__(self):
        self.timmed_process=list()
        self.updateList=list()
        self.updateList_process=list()
        
        self.writer= None
        self.CurrentTime = 0

    def reset(self):
        self.timmed_process=list()
        self.updateList=list()
        self.updateList_process=list()
        
        self.writer= None
        self.CurrentTime = 0

    def isRunning(self):
        return self.CurrentTime >0

        
    def append_updateList(self,obj):
        self.updateList += obj
        self.updateList = list(set(self.updateList))

    def append_updateList_process(self,obj):
        self.updateList_process += obj
        self.updateList_process = list(set(self.updateList_process))

    def register_var(self, module, name, vartype,size):
        vcdvar  = self.writer.register_var(module, name, vartype, size=size)
        return vcdvar

    def change(self, var, value):
        self.writer.change(var, self.CurrentTime, value)

    def run_timed(self,testBench, MaxTime, FileName):
        self.CurrentTime = 0
        objName = getNameOf(testBench)

            
        with open(FileName,"w") as f:
            self.writer =  VCDWriter(f, timescale='1 ns', date='today')
            testBench.set_simulation_param("", objName, self)
            p_list = list()
            for t in self.timmed_process:
                p_list.append({
                        "next_time" : 0,
                        "gen"       : t(),
                        "fun"       : t
                })
            while (self.CurrentTime < MaxTime):
                minNext = 1e100
                for x in p_list:
                    if self.CurrentTime <= x["next_time"]:
                        try:
                            val = next(x["gen"])
                        except StopIteration:
                            x["gen"] = x["fun"]()
                            val = next(x["gen"])

                        x["next_time"] = self.CurrentTime+val.get_time()
                        minNext= min(minNext,val.get_time())

                self.CurrentTime +=  minNext

                while (len(self.updateList)):
                    while (len(self.updateList)):
                        updateList = list(set( self.updateList))
                        self.updateList=list()
                        for x in updateList:
                            x()
                    
                    while (len(self.updateList_process)):
                        updateList_process =  list(set(self.updateList_process))
                        self.updateList_process=list()
                        for x in updateList_process:
                            x()

        self.writer= None
        self.CurrentTime =0


gsimulation = v_simulation()