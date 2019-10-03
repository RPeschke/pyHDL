
import pickle
import os

def LoadDB(FileName):
    try:
        with open(FileName, 'rb') as f:
            data = pickle.load(f) 

    except:
        data={}

    return data



def get_package_for_type(name):
    x = get_package_for_type_internal("build/DependencyBD",name)
    if x: 
        return x
    y = get_package_for_type_internal("build/xgen.db",name)
    if y:
        return y

def get_package_for_type_internal(DataBaseFile,name):
    d = LoadDB(DataBaseFile) 
    n_sp = name.split("(")
    plainName = n_sp[0].strip()
    if len(n_sp) >1:
        print(n_sp[0],"is array type")

    for k in d.keys():
        t = d[k]["Type_Def_detail"]
        e = d[k]["entityDef"]
        if not e:
            for t1 in t:
                if t1["name"] == plainName:
                    return d[k]