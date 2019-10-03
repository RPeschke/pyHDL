import argparse
import os,sys,inspect
import copy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from CodeGen.xgenBase      import *
from CodeGen.xgenPackage   import *
from CodeGen.xgenDB        import *
from CodeGen.xgen_v_class  import *
from CodeGen.xgen_v_enum   import *
from CodeGen.xgen_v_symbol import *

class SerialDataRout_s_state(Enum):
    idle           = 0
    sampleSelect   = 1
    clock_out_data = 2
    received_data  = 3

class axisStream(v_class):
    def __init__(self,AxiName,Axitype):
        super().__init__("axisStream_"+str(AxiName))
        self.valid  = port_out( v_sl() )
        self.last   = port_out( v_sl() )
        self.data   = port_out(copy.deepcopy( Axitype) )
        self.ready  = port_in( v_sl() )
        self.state  = v_enum( SerialDataRout_s_state.idle)


    def sendData(self,z=v_sl(), y=port_out( v_slv(12))):
        if z:
            x= v_slv(12,2)
            y <<  100
        elif x == 2:
            y<< 3

    def isReady(self):
        return self.ready == True

    def setState1(self):
        return self.isReady()

    def setState(self):
        if self.isReady():
            self.sendData()
        elif self.setState1():
            x= 2
            x << 3






xgenAST1 = xgenAST(__file__)

pacl = v_package("sdad",[
    SerialDataRout_s_state,
    axisStream(32,v_slv(32))

])

#xgenAST1.ast_v_classes
fun= list(xgenAST1.extractFunctionsForClass(axisStream(32,v_slv(32)) ,pacl ))
#print(fun)
for f in fun:
    print(f.getHeader("",None))
    print(f.getBody("",None))
#x= list(get_subclasses(tree.body,'v_class'))
#y=list(get_func_args(x[2].body[2]))
#inArgs = get_func_args_list(x[2].body[2] )
#z=list(inArgs)
#ret = z[0]["symbol"].getFuncArg(z[0]["name"],None)
