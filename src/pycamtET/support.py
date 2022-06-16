# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from os import path

from pycamtET.pckgSettings import getSettings
setDict = getSettings()

### input for dataFunctions
_colnames = ['STN_Name','EG_GH_ID','GEOGR2','GEOGR1','ELEVATION','EG_EL','YEAR','MONTH','TIME']+list(range(1,32))
_long_names = {'PRECIP':'precipitation','TMPMIN':'minimum temperature','TMPMAX':'maximum temperature','RD':'rainy days'}
_units = {'PRECIP':'(mm)','TMPMIN':'(\u00B0C)','TMPMAX':'(\u00B0C)','RD':'(-)'}

### input for plotFunctions
_dayEmpty = pd.DataFrame({'MONTH':pd.date_range('2020-01-01','2020-12-31').month,'day':pd.date_range('2020-01-01','2020-12-31').day}).set_index(['MONTH','day'])
_dkEmpty = pd.DataFrame({'MONTH':np.sort(list(range(1,13))*3),'dk':[1,2,3]*12}).set_index(['MONTH','dk'])
_monthEmpty = pd.DataFrame({'MONTH':np.arange(1,13)}).set_index(['MONTH'])
dkTicks1 = pd.Series(['Jan']*3+['Feb']*3+['Mar']*3+['Apr']*3+['May']*3+['Jun']*3+['Jul']*3+['Aug']*3+['Sep']*3+['Oct']*3+['Nov']*3+['Dec']*3)
dkTicks2 = pd.Series([' Dk1',' Dk2',' Dk3']*12)
_dkTicks = dkTicks1+dkTicks2
_monthTicks = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
_seasonTicks = ['Bega','Belg','Kiremt']
_twoMonthEmpty = pd.DataFrame({'YEAR':[1]*12+[2]*12,'MONTH':list(range(1,13))*2}).set_index(['YEAR','MONTH'])
_twoMonthTicks = _monthTicks*2
_colorDict = {'PRECIP':'green','TMPMAX':'red','TMPMIN':'blue','RD':'grey'}

### savedata function
def saveCheck(savePath):
    if savePath == None:
        print('savePath not set. Data not exported to computer.')
        return False
    elif path.isdir(savePath) == False:
        print('The provided savePath does not exist or is not a folder on your computer. Please provide a valid path to a folder.')
        return False
    else:
        return True

def vecAvgDf(dfwind,groupby):
    """
    Creates a grouped vector-average windspeed and direction based on a DataFrame with WINSPD and WINDIR columns. Argument groupby is passed on to the by= argument of the groupby function.
    """

    df = dfwind.copy()
    
    df['YEAR'] = df.dateTime.dt.year
    df['MONTH'] = df.dateTime.dt.month
    
    df.loc[df.WINDIR==0,'WINSPD'] = 0
    
    mat_dir = (270-df.WINDIR)*np.pi/180  
    u = -df.WINSPD*np.cos(mat_dir)
    v = -df.WINSPD*np.sin(mat_dir)
    df['uwind'] = u
    df['vwind'] = v

    dfavg = df.groupby(by=groupby).mean().get(['uwind','vwind'])
    dfavg['WINSPD'] = np.sqrt(dfavg.uwind**2+dfavg.vwind**2)
    mat_dir_avg = np.arctan2(dfavg.vwind,dfavg.uwind)
    wdir = np.round((mat_dir_avg*-1)*180/np.pi+90,0)
    wdir[wdir<0]=wdir[wdir<0]+360
    dfavg['WINDIR'] = wdir.round(0)
    
    dfavg.loc[:,['uwind','vwind','WINSPD']] = dfavg.get(['uwind','vwind','WINSPD']).round(2)
    
    return dfavg

def vecAvg(ws,wdir):
    """
    Creates one vector-average windspeed and direction based on a collection of values.
    """
    ws = np.array(ws)
    wdir = np.array(wdir)
    mat_dir = (270-wdir)*np.pi/180
    u = -ws*np.cos(mat_dir)
    v = -ws*np.sin(mat_dir)
    u_avg = np.nanmean(u)
    v_avg = np.nanmean(v)
    ws_avg = np.round(np.sqrt(u_avg**2+v_avg**2),2)
    mat_dir_avg = np.arctan2(v_avg,u_avg)
    wdir_avg = np.round((mat_dir_avg*-1)*180/np.pi+90,0)
    # if wdir_avg<0:
    #     wd_avg+360
    # print("u: %s, v: %s, ws: %s, md: %s,wdir: %s" % (u_avg,v_avg,ws_avg,mat_dir_avg,wdir_avg))
    return ws_avg,wdir_avg

def stationInfo(filePath,updateAll=False):
    from pycamtET.pckgSettings import getSettings
    from pandas import read_csv
    from pathlib import Path
    siPath = getSettings()['pckgsdataPath']+'/stationInfo.csv'
    if type(updateAll)!=bool:
        print('Please only provide a boolean True or False for updateAll.')
        return
    if Path(filePath).exists()==False:
        print('Please provide a valid filepath.')
        return
    df = read_csv(filePath,usecols=[0,1,2,3,4])
    df = df.set_axis(labels=['STN_Name','EG_GH_ID','GEOGR2','GEOGR1','ELEVATION'],axis=1)
    df.loc[:,'STN_Name'] = df.STN_Name.str.title().str.strip()
    si = df.drop_duplicates(subset=['STN_Name'],ignore_index=True)
    
    if Path(siPath).exists():
        siOld = read_csv(siPath)
        if updateAll:
            print('updateAll set to True. All stationinfo of stations in the provided file will be updated.')
            siNew = si
            siOld = siOld[~siOld.STN_Name.isin(si.STN_Name)]
        else:
            siNew = si[~si.STN_Name.isin(siOld.STN_Name)]
    else:
        siNew = si
        siOld = si.iloc[:0,:]
    
    if len(siNew) == 0:
        print('No new stationinfo. Nothing is updated. To update all anyway, set updateAll to True.')
        return siOld.set_index('STN_Name')
        
    siNew = siNew.set_index('STN_Name').sort_index()    
    
    if len(siOld)==0:
        print('No previous station data found, or updateAll=True. New station data saved.')
        siNew.to_csv(siPath)
        return siNew
    
    siOld = siOld.set_index('STN_Name')
    siAll = siNew.append(siOld)
    siAll = siAll.sort_index()
    print('Data combined with previous stationinfo. All data saved.')
    siAll.to_csv(siPath)
    return siAll

def rmGridData():
    from pckgSettings import getSettings
    from shutil import rmtree
    from pathlib import Path
    gridpath = getSettings()['pckgsdataPath']+'/griddata'
    if Path(gridpath).exists():
        rmtree(gridpath)