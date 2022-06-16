__all__ = ['dataFunctions','plotFunctions','mapFunctions']

from .pckgSettings import initSettings as _initSettings
setDict = _initSettings(str(__file__))

from . import dataFunctions
from . import plotFunctions

import importlib as _importlib
import pathlib as _pathlib

_gpd_spec = _importlib.util.find_spec("geopandas")
if _gpd_spec is None:
    print('Package geopandas is not installed. example_package.mapFunctions cannot be used.')
else:
    if _pathlib.Path(setDict['adm3Path']).exists()==False:
        print('File location of adm3 (ET districts) shape file not found at '+setDict['adm3Path']+'. Map abilities cannot be used.\n',
              'If you have the shape file, put it at that location, or set the full path by using pckgSettings.setSettings(adm3Path="path/to/adm3shapefiles")')
    else:
        if _pathlib.Path(setDict['adm2Path']).exists()==False:
            print('File location of adm2 (ET zones) shape file not found at '+setDict['adm2Path']+'. Map abilities cannot be used.\n',
                  'If you have the shape file, put it at that location, or set the full path by using pckgSettings.setSettings(adm2Path="path/to/adm2shapefiles")')
        else:
            if _pathlib.Path(setDict['adm1Path']).exists()==False:
                print('File location of adm1 (ET regions) shape file not found at '+setDict['adm1Path']+'. Map abilities cannot be used.\n',
                      'If you have the shape file, put it at that location, or set the full path by using pckgSettings.setSettings(adm1Path="path/to/adm1shapefiles")')
            else:
                if _pathlib.Path(setDict['adm0Path']).exists()==False:
                    print('File location of adm0 (full Ethiopia) shape file not found at '+setDict['adm0Path']+'. Map abilities cannot be used.\n',
                          'If you have the shape file, put it at that location, or set the full path by using pckgSettings.setSettings(adm0Path="path/to/adm0shapefiles")')
                else:
                    from . import mapFunctions