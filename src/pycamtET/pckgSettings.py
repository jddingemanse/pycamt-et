# -*- coding: utf-8 -*-
import pathlib
import json

def initSettings(initPath):
    parent = pathlib.Path(initPath).parent
    pckgsdata = parent/'pckgdata'
    setfile = pckgsdata/'settings.txt'
    pycamt = pathlib.Path.home()/'Documents/PyCAMT'
    shapePath = pycamt/'shapefiles'
    dataPath = pycamt/'data'
    outPath = pycamt/'output'
    
    ## Create folders in the Documents folder, and create pckgsdata folder in the source code folder
    if shapePath.exists()==False:
        shapePath.mkdir(parents=True)
    if dataPath.exists()==False:
        dataPath.mkdir(parents=True)
    if outPath.exists()==False:
        outPath.mkdir(parents=True)
    if pckgsdata.exists()==False:
        pckgsdata.mkdir()

    if setfile.exists():
        handler = open(setfile,'r')
        data = handler.read()
        handler.close()
        settingsDict = json.loads(data.replace('\'','\"'))
    else:
        settingsDict = {'adm0Path':str(shapePath)+'\ETadm0.zip',
                        'adm1Path':str(shapePath)+'\ETadm1.zip',
                        'adm2Path':str(shapePath)+'\ETadm2.zip',
                        'adm3Path':str(shapePath)+'\ETadm3.zip',
                        'pckgsdataPath':str(pckgsdata),
                        'pycamtPath':str(pycamt),
                        'dataPath':str(dataPath),
                        'outPath':str(outPath)}
        handler = open(setfile,'w')
        handler.write(str(settingsDict))
        handler.close()
    
    handler = open(setfile,'w')
    handler.write(str(settingsDict))
    handler.close()
    return settingsDict

def setSettings(**kwargs):
    import pycamtET.support as sp
    parent = pathlib.Path(sp.__file__).parent
    pckgsdata = parent/'pckgdata'
    setfile = pckgsdata/'settings.txt'
    pycamt = pathlib.Path.home()/'Documents/PyCAMT'
    shapePath = pycamt/'shapefiles'
    dataPath = pycamt/'data'
    outPath = pycamt/'output'
    
    ## Create folders in the Documents folder, and create pckgsdata folder in the source code folder
    if shapePath.exists()==False:
        shapePath.mkdir(parents=True)
    if dataPath.exists()==False:
        dataPath.mkdir(parents=True)
    if outPath.exists()==False:
        outPath.mkdir(parents=True)
    if pckgsdata.exists()==False:
        pckgsdata.mkdir()

    if setfile.exists():
        handler = open(setfile,'r')
        data = handler.read()
        handler.close()
        settingsDict = json.loads(data.replace('\'','\"'))
    else:
        settingsDict = {'adm0Path':str(shapePath)+'\ETadm0.zip',
                        'adm1Path':str(shapePath)+'\ETadm1.zip',
                        'adm2Path':str(shapePath)+'\ETadm2.zip',
                        'adm3Path':str(shapePath)+'\ETadm3.zip',
                        'pckgsdataPath':str(pckgsdata),
                        'pycamtPath':str(pycamt),
                        'dataPath':str(dataPath),
                        'outPath':str(outPath)}
        handler = open(setfile,'w')
        handler.write(str(settingsDict))
        handler.close()
    
    settingsDict.update(kwargs)
    handler = open(setfile,'w')
    handler.write(str(settingsDict))
    handler.close()
    return settingsDict

def getSettings():
    import pycamtET.support as sp
    parent = pathlib.Path(sp.__file__).parent
    pckgsdata = parent/'pckgdata'
    setfile = pckgsdata/'settings.txt'
    if setfile.exists():
        handler = open(setfile,'r')
        data = handler.read()
        handler.close()
        settingsDict = json.loads(data.replace('\'','\"'))
        return settingsDict
    else:
        print(str(setfile)+' not found. Please run dataFunctions.setSettings() to create the settings file.')
