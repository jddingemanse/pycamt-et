# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from os import path
import os

from pycamtET.pckgSettings import getSettings
setDict = getSettings()

from matplotlib.patches import Patch
_legend_elements = [Patch(facecolor='red', edgecolor='red',label='under'),
                   Patch(facecolor='yellow', edgecolor='yellow',label='normal'),
                   Patch(facecolor='green', edgecolor='green',label='over')]

# geopandas-dependent
geodata=True

try:
    import geopandas as gpd
except:
    print('Importing package geopandas not successful. Map abilities can not be used. To use these abilities, install the package geopandas')
    geodata=False
if geodata:
    try:
        _adm_d = gpd.read_file(setDict['adm3Path'])
        _adm_m = _adm_d.to_crs(epsg=20137)
        _metercrs = _adm_m.crs
        _adm_d = gpd.read_file(setDict['adm3Path'])
    except:
        print('File location of adm3 (ET districts) shape file not found at '+setDict['adm3Path']+'. Map abilities cannot be used.\n',
              'If you have the shape file, set the full path by using pckgSettings.setSettings(adm3Path="path/to/adm3shapefiles")')

    try:
        _adm2_d = gpd.read_file(setDict['adm2Path'])
    except:
        print('File location of adm2 (ET zones) shape file not found at '+setDict['adm2Path']+'. Map abilities cannot be used.\n',
              'If you have the shape file, set the full path by using pckgSettings.setSettings(adm2Path="path/to/adm2shapefiles")')

    try:
        _adm1_d = gpd.read_file(setDict['adm1Path'])
    except:
        print('File location of adm1 (ET regions) shape file not found at '+setDict['adm1Path']+'. Map abilities cannot be used.\n',
              'If you have the shape file, set the full path by using pckgSettings.setSettings(adm1Path="path/to/adm1shapefiles")')

    try:
        _adm0_d = gpd.read_file(setDict['adm0Path'])
    except:
        print('File location of adm0 (full ET) shape file not found at '+setDict['adm0Path']+'. Map abilities cannot be used.\n',
              'If you have the shape file, set the full path by using pckgSettings.setSettings(adm0Path="path/to/adm0shapefiles")')

    from shapely.ops import unary_union

def gridcalculate(gpdshape,areaname,gridsize=100):    
    dirName = setDict['pckgsdataPath']+'/griddata'
    pathName = dirName+'/'+areaname+'Grid.csv'

    
    if path.isfile(pathName):
        print(areaname+' gridfile read from computer.')
        griddf = pd.read_csv(pathName)
    else:
        if path.isdir(dirName)==False:
            os.mkdir(dirName)
        print('Grid not yet calculated before. It will be calculated now, this will take some time...')
        shape_d = unary_union(gpdshape.geometry)
    
        xmin = shape_d.bounds[0]
        ymin = shape_d.bounds[1]
        xmax = shape_d.bounds[2]
        ymax = shape_d.bounds[3]
    
        xpoints = np.linspace(xmin,xmax,gridsize)
        ypoints = np.linspace(ymin,ymax,gridsize)
        x2d_d,y2d_d = np.meshgrid(xpoints,ypoints)
        x1d_d = x2d_d.reshape(x2d_d.size)
        y1d_d = y2d_d.reshape(y2d_d.size)
        points_d=gpd.points_from_xy(x1d_d,y1d_d,crs='EPSG:4236')
        bool1d = points_d.within(shape_d) 
            
        points_m=points_d.to_crs(_metercrs)
    
        griddf = pd.DataFrame(index=range(gridsize**2))
        griddf.loc[:,'x_d'] = x1d_d
        griddf.loc[:,'y_d'] = y1d_d
        griddf.loc[:,'bool1d'] = bool1d
        griddf.loc[:,'x_m'] = points_m.x
        griddf.loc[:,'y_m'] = points_m.y
    
        griddf.to_csv(pathName,index=False)
        print(areaname+' gridcalculation finished and saved on computer to save calculation time for the next time.')

    return griddf