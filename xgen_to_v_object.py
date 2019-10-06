from .xgenBase import *
from .xgen_v_enum import * 
from .xgen_v_symbol import * 

def to_v_object(ObjIn):
    if issubclass(type(ObjIn),vhdl_base):
        return ObjIn
    elif type(ObjIn).__name__ == "EnumMeta":
        return v_enum(ObjIn)
    elif type(ObjIn).__name__ == 'bool':
        return v_symbol("boolean", str(ObjIn))
    elif type(ObjIn).__name__ == 'v_Num':
        return v_symbol("integer", str(ObjIn))
    elif type(ObjIn).__name__ == 'str':
        return v_symbol("undef", str(ObjIn))

    elif ObjIn == None:
        return v_symbol("None", str(ObjIn))

        
    raise Exception("unknown type")