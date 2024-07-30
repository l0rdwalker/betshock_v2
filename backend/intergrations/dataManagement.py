import os
import sys
import importlib

def writeFile(path,content):
    with open(path, "a") as myfile:
        myfile.write(f'\n{content}')

def readCache(path):
    try:
        data = []
        with open(path, 'r') as file:
            for line in file:
                data.append(line.strip())
        return data
    except:
        return []
    
def getModuleByPath(path,name,database_obj,additionalAttributes=None):
    fileName = name+'.py'
    moduleFilePath = os.path.join(path,fileName)

    loader = importlib.machinery.SourceFileLoader(name, moduleFilePath)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    
    loader.exec_module(module)
    classInstance = getattr(module,name)

    if additionalAttributes == None:
        return classInstance(database_obj)
    else:
        return classInstance(additionalAttributes,database_obj)