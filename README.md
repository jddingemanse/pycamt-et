# pycamtET
In the package pycamtET, relevant data processing tools for Ethiopian meteorological data are bundled. The package [pycamtETinterface](https://github.com/jddingemanse/pycamtETinterface) holds code for a Jupyter-Notebook widget interface that can operate the functions of pycamtET.
Both packages are fully under development, so you can expect regular changes.

## Installation
First, make sure git is installed.
```
conda install git
```
If git is installed, you can install pycamtET with:
```
pip install git+https://github.com/jddingemanse/pycamtET.git
```

## Package structure
Functions for dataprocessing and plotting are stored in three different modules: .dataFunctions, .plotFunctions and .mapFunctions. Functions from .datafunctions can be used to process data. The processed data can be plotted as timeseries data with different functions under .plotFunctions, and on a map with different functions under .mapFunctions.

Processing and plotting of data requires as input a datafile with meteorological station data from the Ethiopian Meteorology Institute. The package assumes this data is a .csv file with 40 columns: 9 columns with identifying data (location, element, year, month, etcetera) and 31 columns of 31 days per month.

## Dependencies
In pycamtET, all .mapfunctions are depending on the package [Geopandas](https://anaconda.org/conda-forge/geopandas).

One of the .mapFunctions is kriMap(); that function is depending on the package [pykrige](https://anaconda.org/conda-forge/pykrige).

In the .plotFunctions, there is the function windRose(); that function is depending on the package [windrose](https://anaconda.org/conda-forge/windrose).

## Use examples
### Plot of one year versus other years
To create a plot for the precipitation in the year 2015 versus all other years in your datafile, for the station Assela, with a dekadal-timestep, you must:
- load and preprocess data with dataFunctions.dataLoad()
- select data for the station Assela with the function dataFunctions.locSelect()
- process the precipitation data of Assela to dekadal-averages with dataFunctions.timeData()
- plot this processed data with plotFunctions.recentHistoric()
```
from pycamtET import dataFunctions as dFu, plotFunctions as pFu
filepath = 'pathtoyourdatafile'
dfAll = dFu.dataLoad(filePath)
dfOne = dFu.locSelect(dfAll,'Assela')
dfTime = dFu.timeData(dfOne,'PRECIP','dekadal')
pFu.recentHistoric(dfTime,2015)
```
If you want to save the plot, at a location of your choice, you can include the argument savePath, with a valid path to a folder in which you want to save the plot:
```
pFu.recentHistoric(dfTime,2015,savePath='pathToFolderWhereYouWantToSave')
```
Of course, this only works if there is precipitation data for the station Assela for the year 2015 in the file you provided.

### Inverse Distance Weighting
To create a map of Oromia for maximum temperature, for the season Bega of the year 2010, interpolated based on Inverse Distance Weighting, you must:
- load and preprocess data with dataFunctions.dataLoad()
- select data for all locations, for maximum temperature, for Bega 2010 with dataFunctions.locData()
- plot this processed data with mapFunctions.idwMap()
```
from pycamtET import dataFunctions as dFu, mapFunctions as mFu
filepath = 'pathtoyourdatafile'
dfAll = dFu.dataLoad(filePath) 
dfLoc = dFu.locData(dfAll,'PRECIP',2010,season='Bega')
mFu.idwMap(dfLoc,region='Oromia')
```
Of course, this only works if there is maximum temperature data for multiple stations, for the chosen year and season, in the file you provided.

### Windrose
To create a windrose, for station Abomsa, for the year 2012, month 3, you must:
- load and preprocess data with dataFunctions.dataLoad()
- additionally process the data towards a DataFrame that has the columns WINSPD and WINDIR (this is not yet implemented into the package, so the user must do this 'manually'; example code is shown below)
- turn this processed data into a windrose with plotFunctions.windRose()
```
from pycamtET import dataFunctions as dFu, plotFunctions as pFu
filepath = 'pathtoyourdatafile'
df = dFu.dataLoad(filepath)
wind = df[df.EG_EL == 'WINSPD'].drop_duplicates(subset=['STN_Name','dateTime']).set_index(['STN_Name','dateTime']).rename(columns={'value':'WINSPD'}).get(['season','seasonyear','dk','WINSPD'])
wind.loc[:,'WINDIR'] = df[df.EG_EL == 'WINDIR'].drop_duplicates(subset=['STN_Name','dateTime']).set_index(['STN_Name','dateTime']).rename(columns={'value':'WINDIR'}).get(['WINDIR'])
wind = wind.reset_index()
pFu.windRose(wind,'Abomsa',2012,month=3)
```
Of course, this only works if there is wind (direction and speed) data for the station Abomsa for March 2015 in the file you provided.
