# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 12:03:42 2022

Ideas:
    - Add a DF format check
    - Solve warnings

Remarks:
    - What to do with multiple times on the same day?
    - Seasonal: is Bega 2015 the months 1, 10-12 of 2015, or 10-12 2015 and 1-2016?
    - What about missing data and Rainy Days?

@author: jandirk
"""
import pandas as _pd
import numpy as _np

from pycamtET.support import _colnames,_long_names,_units

def dataLoad(filePath,dataChoice='values'):
    """   
    Parameters
    ----------
    filePath : STR
        filePath including filename of the data to load. A normal EMI data-format
        is assumed.
    dataChoice : STR, 'values' or 'metadata'
        If values: returns the values with relevant identifier columns
        If metadata: returns stations with relevant metadata
    
    For values, any non-numeric value is turned into NaN.

    Returns
    -------
    
    Pandas DataFrame with columns, if dataChoice='values': 
        ['STN_Name', 'EG_EL', 'YEAR', 'MONTH', 'TIME', 'day', 'value', 'date','season','dk']
        The column value holds the value from the original Day1-Day31 columns.
                                   if dataChoice = 'metadata':

    """
    df = _pd.read_csv(filePath,dtype='object').iloc[:,:40]
    df = df.set_axis(labels=_colnames,axis=1)
    df.loc[:,'STN_Name'] = df.STN_Name.str.title().str.strip()
    from pycamtET.support import stationInfo
    stationInfo(filePath)
    if dataChoice == 'values':
        df = df.drop(columns=df.columns[1:5])
        # repair some time values without ':'
        df.loc[~df.TIME.str.contains(':'),'TIME']=df[~df.TIME.str.contains(':')].TIME.str.slice_replace(-2,-2,':')
        # turn all remaining na TIMES into 9:00
        df.loc[:,'TIME'] = _pd.to_datetime(df.TIME,format='%H:%M',errors='coerce').fillna(_pd.to_datetime('9:00')).dt.hour
        df = df.melt(id_vars=df.columns[:5],var_name='day')
        df.loc[:,'YEAR'] = _pd.to_numeric(df.YEAR)
        df.loc[:,'MONTH'] = _pd.to_numeric(df.MONTH)
        dftime = df.get(['YEAR','MONTH','day','TIME']).rename(columns={'TIME':'hour'})
        df['dateTime']=_pd.to_datetime(dftime,errors='coerce')
        df.dropna(subset=['dateTime'],inplace=True)
        df['date'] = _pd.to_datetime(df.dateTime.dt.date)

        df['value'] = _pd.to_numeric(df.value,errors='coerce')
        df.sort_values(by=['STN_Name','EG_EL','dateTime'],inplace=True,ignore_index=True)

        # Add season and Dk
        df['season']=_pd.cut(df.MONTH,[0,1,5,9,12],labels=['Bega','Belg','Kiremt','Bega1']).replace('Bega1','Bega')
        df['seasonyear'] = df.YEAR
        df.loc[df.MONTH==1,'seasonyear'] = df.YEAR[df.MONTH==1]-1
        df['dk'] = _pd.cut(df.day,[0,10,20,31],labels=[1,2,3])
        
        df.filePath = filePath
        return df
    elif dataChoice == 'metadata':
        
        df = df.drop_duplicates(subset=['STN_Name'],ignore_index=True).iloc[:,:5]
        #df = df.drop_duplicates(subset=['GEOGR2','GEOGR1'],ignore_index=True)
        df.filePath = filePath
        return df
    else:
        print('dataChoice not clear. Please select \'values\' or \'metadata\'')

def locSelect(dataFrame,stationName='Assela'):
    """
    From a dataFrame resulting from the function dataLoad(), select the data for
    one station, with the different elements as different columns.

    Parameters
    ----------
    dataFrame : _pd DataFrame
        The dataFrame that results from a succesful use of the function dataLoad.
    stationName : STR, optional
        Give the stationname. The default is 'Assela'.

    Multiple data points on the same day are averaged into one value per day.

    Returns
    -------
    Pandas DataFrame with the data for specified station, elements as columns, indexed by date.

    """    
    df = dataFrame
    stationName = stationName.title()
    
    if len(df[df.STN_Name==stationName])==0:
        print('The provided stationName is not found in the provided DataFrame.')
        print('Available stationnames are: '+str(df.STN_Name.unique()))
        return
    else:
        elements = df.EG_EL[df.STN_Name==stationName].unique()
        dfSeasonDk = df[df.STN_Name==stationName].get(['date','season','seasonyear','dk']).drop_duplicates(subset=['date']).set_index(['date'])
        dfDay = df[(df.STN_Name==stationName)&(df.EG_EL==elements[0])].resample(rule='D',on='date').mean()
        dfDay = dfDay.rename(columns={'value':elements[0]})
        for i in range(1,len(elements)):
            dfAdd = df[(df.STN_Name==stationName)&(df.EG_EL==elements[i])].resample(rule='D',on='date').mean()
            dfDay[elements[i]] = dfAdd.value
        
        if 'PRECIP' in elements:
            dfDay['RD'] = _pd.to_numeric(_pd.cut(dfDay.PRECIP,[-1,1,dfDay.PRECIP.max()],labels=[0,1]))
        
        dfDay['YEAR'] = dfDay.index.year
        dfDay['MONTH'] = dfDay.index.month
        dfDay['day'] = dfDay.index.day
        dfDay['season'] = dfSeasonDk['season']
        dfDay['dk'] = dfSeasonDk['dk']
        dfDay = dfDay.drop(columns=['TIME'])
        
        #Reorganize order of columns
        timecols = ['YEAR','seasonyear','season','MONTH','dk','day']
        elcols = dfDay.columns[~dfDay.columns.isin(timecols)].to_list()
        cols = timecols+elcols
        dfDay = dfDay[cols]
        
        dateMin = str(dfDay.index.date.min())
        dateMax = str(dfDay.index.date.max())

        missingStr = ''
        for i in range(len(elcols)):
            missing=str(round(dfDay[elcols[i]].isna().mean()*100,1))+'%'
            missingStr += elcols[i] + ' (' + missing + ' NaN)'
            if i<len(elcols)-2:
                missingStr += ', '
            elif i<len(elcols)-1:
                missingStr += ' and '
            else:
                missingStr += '.'      
        
        print('For '+stationName+', data is found from '+dateMin+' to '+dateMax+'.')
        print('In this period, there is data for elements '+missingStr)
        
        dfDay.stationName = stationName
        
        return dfDay

def timeData(dataFrame,element,timeperiod):    
    """
    This function creates a DataFrame with relevant data for timeperiod analysis, for timeperiod dekadal, month, season or year.
    Per period, the element's data for that period, the average & standard deviation for all similar periods, the total number of days in that period and the number of days with obseration in that period are given.
    For rainfall ('PRECIP') and rainy days ('RD'), the sum is given. For temperatures ('TMPMIN' or 'TMPMAX'), the average is given.

    Parameters
    ----------
    dataFrame : pandas DataFrame
        A single station dataframe resulting from the function locSelect.
    element : string
        The element of which data needs to be organized. Options: 'TMPMIN','TMPMAX','PRECIP','RD'.
    timeperiod: string
        The timeperiod for which the data needs to be organized. Options: 'dekadal','month','season' or 'year'.
        
    Returns
    -------
    Pandas DataFrame with element timperiod data.

    """
    df = dataFrame
    stationName = df.stationName

    options = ['year','season','month','dekadal','day']
    
    element_options = ['TMPMIN','TMPMAX','PRECIP','RD']
    
    if element not in element_options:
        print('The chosen element is not (yet) implemented./nCurrently implemented are one of '+str(element_options))
        return
    if (element not in df.columns):
        print('The provided DataFrame misses column \''+element+'\'.\n',
              'Please provide another DataFrame or select another element.\n',
              'The provided DataFrame only has elements '+str(df.columns.to_list()[6:]))
        return
    if (timeperiod not in options):
        print('The provided timeperiod \''+timeperiod+'\' is not one of the options.\n',
              'Please select one of the following '+str(options))
        return
    
    if timeperiod == 'day':
        getList = ['YEAR','MONTH','day',element]
        groupList = ['YEAR','MONTH','day']
        aggGroupList = ['MONTH','day']        
    elif timeperiod == 'dekadal':
        getList = ['YEAR','MONTH','dk',element]
        groupList = ['YEAR','MONTH','dk']
        aggGroupList = ['MONTH','dk']
    elif timeperiod =='month':
        getList = ['YEAR','MONTH',element]
        groupList = ['YEAR','MONTH']
        aggGroupList = ['MONTH']    
    elif timeperiod =='season':
        getList = ['seasonyear','season',element]
        groupList = ['seasonyear','season']
        aggGroupList = ['season']
    else:
        getList = ['YEAR',element]
        groupList = ['YEAR']
    
    dfEL = df.get(getList)
    if (element == 'PRECIP') or (element == 'RD'):
        periodEL = dfEL.groupby(by=groupList).sum()
    elif (element == 'TMPMIN') or (element == 'TMPMAX'):
        periodEL = dfEL.groupby(by=groupList).mean()
    
    nNona = dfEL.groupby(by=groupList).count()
    
    if timeperiod != 'year':
        periodMean = periodEL.groupby(level=aggGroupList).mean().rename(columns={element:element+'avg'})
        periodStd = periodEL.groupby(level=aggGroupList).std().rename(columns={element:element+'std'})
        periodEL = periodEL.join(periodMean,on=aggGroupList)
        periodEL = periodEL.join(periodStd,on=aggGroupList)
    else:
        periodEL[element+'avg'] = periodEL[element].mean()
        periodEL[element+'std'] = periodEL[element].std()
            
    periodEL=periodEL.reset_index()
    
    # To get missing data info; only if period is not day
    if timeperiod!='day':
        timecols = periodEL.get(groupList)
        
        if timeperiod == 'dekadal':
            datetime = _pd.to_datetime(timecols.rename(columns={'YEAR':'year','MONTH':'month','dk':'day'}))
            monthDays = _pd.Series(datetime.dt.days_in_month,index=periodEL.index)
            dekaCons = [
                        (periodEL.dk<=2),
                        (periodEL.dk==3)&(monthDays==28),
                        (periodEL.dk==3)&(monthDays==29),
                        (periodEL.dk==3)&(monthDays==30),
                        (periodEL.dk==3)&(monthDays==31)
                        ]
            dekaVals = [10,8,9,10,11]
            periodDays = _pd.Series(_np.select(dekaCons,dekaVals),index=periodEL.index)
        elif timeperiod == 'month':
            timecols.loc[:,'day'] = 1
            datetime = _pd.to_datetime(timecols.rename(columns={'YEAR':'year','MONTH':'month'}))
            periodDays = _pd.Series(datetime.dt.days_in_month,index=periodEL.index)
        elif timeperiod == 'season':
            timecols.loc[:,'day'] = 1
            timecols.loc[:,'month'] = 1
            datetime = _pd.to_datetime(timecols.rename(columns={'seasonyear':'year'}).get(['year','month','day'])) 
            seasCons = [
                (timecols.season=='Bega'),
                (timecols.season=='Kiremt'),
                (timecols.season=='Belg')&(datetime.dt.is_leap_year==False),
                (timecols.season=='Belg')&(datetime.dt.is_leap_year)
            ]
            seasVals = [31*3+30,30*2+31*2,28+2*31+30,29+2*31+30]
            periodDays = _pd.Series(_np.select(seasCons,seasVals),index=periodEL.index)
        else:
            timecols.loc[:,'day'] = 1
            timecols.loc[:,'month'] = 1
            datetime = _pd.to_datetime(timecols.rename(columns={'YEAR':'year'}).get(['year','month','day'])) 
            yearCons = [(datetime.dt.is_leap_year),(datetime.dt.is_leap_year==False)]
            periodDays = _pd.Series(_np.select(yearCons,[366,365]),index=periodEL.index)
        nNona = _pd.Series(nNona[element].values,index=periodEL.index)
        periodEL['periodDays'] = periodDays
        periodEL['nonaFrac'] = nNona/periodDays
        
        periodEL = periodEL[periodEL.nonaFrac>0]
    
    if timeperiod=='day':
        periodEL = periodEL.dropna(subset=[element])
    
    print(timeperiod+' data for '+element+' are calculated for station '+stationName)
    if timeperiod=='season':
        print('Seasonal timeperiod is used. The year in the DataFrame for season Bega means the last three months of that year and the first month of the next year.')
        #rename seasonyear column and sort by season Belg->Kiremt->Bega
        periodEL = periodEL.rename(columns={'seasonyear':'YEAR'})
        periodEL.loc[:,'season'] = _pd.Categorical(periodEL.season,['Belg','Kiremt','Bega'])
        periodEL = periodEL.sort_values(by=['YEAR','season'])
        
        
    dfReturn = periodEL.set_index(_np.arange(len(periodEL)))
    # general metadata
    dfReturn.element = element
    dfReturn.long_name = _long_names[element]
    dfReturn.unit = _units[element]
    dfReturn.dimension = 'temporal'
    
    # timeData metadata
    dfReturn.stationName = stationName
    dfReturn.timeperiod = timeperiod
    
    # locData metadata
    dfReturn.yearID = None
    dfReturn.seasonID = None
    dfReturn.monthID = None
    dfReturn.dkID = None
    
    return dfReturn

def locData(dataFrame,element,year,season=None,month=None,dekadal=None):
    """
    From a dataFrame resulting from the function dataLoad(), select the data for one element of a specific timeperiod, for all available stations.
    The timeperiod can be a year, a specific year-season, a specific year-month or a specific year-month-dekadal.
    For the specified element, the station value of the specified timeperiod, and the average and standard deviation for that station of all comparable timeperiods are provided.
    For rainfall ('PRECIP') and rainy days ('RD'), the sum is given. For temperatures ('TMPMIN' or 'TMPMAX'), the average is given.
   
    Parameters
    ----------
    dataFrame : _pd DataFrame
        The dataFrame that results from a succesful use of the function dataLoad.
    element : STR
        The element of which data needs to be organized. Options: 'TMPMIN','TMPMAX','PRECIP','RD'.
    year : INT
        The year for which data needs to be retrieved.
    season : None or STR, optional
        If None, it is not used. If provided, it must be one of 'Kiremt', 'Bega' or 'Belg'.
    month: None or INT, optional
        If None, it is not used. The month-number for which data needs to be retrieved. To be used for a certain month, or in combination with dekadal.
    dekadal : None, or INT, optional
        If None, it is not used. The dekadal number (1,2 or 3) for which data needs to be retrieved. If used, also month needs to be provided.

    Returns
    -------
    Pandas DataFrame with the data for the specified timeperiod, indexed by stationname.

    """   
    df = dataFrame.copy()
    
    element_options = ['TMPMIN','TMPMAX','PRECIP','RD']
    
    if element not in element_options:
        print('The chosen element is not (yet) implemented./nCurrently implemented are one of '+str(element_options))
        return
    if (element not in df.EG_EL.unique()):
        if (element!='RD') or ('PRECIP' not in df.EG_EL.unique()):
            print('The provided DataFrame misses data of \''+element+'\'.\n',
                  'Please provide another DataFrame or select another element.')
            return
        
    if (year not in df.YEAR.unique()):
        print('The chosen year is not in the provided dataframe.\n',
              'Make sure that the year is provided as integer')
        return
    elif (dekadal != None): 
        if (month==None):
            print('Dekadal supplied, but month is not chosen.\n',
                  'Please only select a dekadal in combination with a month.')
            return
        elif month not in df.MONTH[df.YEAR==year].values:
            print('The chosen month-year does not exist.')
            return
        elif dekadal not in df.dk[(df.YEAR==year)&(df.MONTH==month)].values:
            print('The chosen dk-month-year does not exist.')
            return
        else:
            dkList = [dekadal]
            monthList = [month]
            seasonList = ['Belg','Bega','Kiremt']
    elif month != None:
        if month not in df.MONTH[df.YEAR==year].values:
            print('The chosen month-year does not exist.')
            return
        else:
            seasonList=['Belg','Bega','Kiremt']
            monthList = [month]
            dkList = [1,2,3]
    elif season != None:
        if season not in df.season[df.YEAR==year].values:
            print('The chosen season-year does not exist.\n',
                  'Please provide strings belg, bega or kiremt')
            return
        else:
            df.loc[:,'YEAR'] = df.seasonyear
            seasonList = [season]
            monthList = [1,2,3,4,5,6,7,8,9,10,11,12]
            dkList = [1,2,3]
    else:
        dkList = [1,2,3]
        monthList = [1,2,3,4,5,6,7,8,9,10,11,12]
        seasonList = ['Belg','Bega','Kiremt']
    
    if element == 'RD':
        df['value'] = _pd.to_numeric(_pd.cut(df.value,[-1,1,df.value.max()],labels=[0,1]))
        df.EG_EL.replace('PRECIP','RD',inplace=True)
            
    subdf = df[(df.YEAR==year)&(df.season.isin(seasonList))&(df.MONTH.isin(monthList))&(df.dk.isin(dkList))&(df.EG_EL==element)]
    subdfAll = df[(df.season.isin(seasonList))&(df.MONTH.isin(monthList))&(df.dk.isin(dkList))&(df.EG_EL==element)]
        
    grouper = subdf.groupby(by=['STN_Name'])
    grouperAll = subdfAll.groupby(by=['STN_Name','YEAR'])
    if (element=='PRECIP') or (element=='RD'):
        dfLoc = grouper.sum()
        dfLocAll = grouperAll.sum()
    else:
        dfLoc = grouper.mean()
        dfLocAll = grouperAll.mean()
    dfLoc[element+'avg'] = dfLocAll.groupby(by=['STN_Name']).mean()['value']
    dfLoc[element+'std'] = dfLocAll.groupby(by=['STN_Name']).std()['value']
    dfLoc = dfLoc.rename(columns={'value':element})

    dfLoc = dfLoc.get([element,element+'avg',element+'std'])
    
    if month == None:
        if season == None:
            timeStr = str(year)
        else:
            timeStr = str(year)+' '+season
    elif dekadal == None:
        timeStr = str(year)+'-'+str(month)
    else:
        timeStr = str(year)+'-'+str(month)+' dk'+str(dekadal)

    nLoc = str(len(dfLoc))
    
    print('Data for element '+element+' is calculated for '+timeStr,
          ' for '+nLoc+' locations.')
    
    dfReturn = dfLoc
    # general metadata
    dfReturn.element = element
    dfReturn.long_name = _long_names[element]
    dfReturn.unit = _units[element]
    dfReturn.dimension = 'spatial'
    
    # timeData metadata
    dfReturn.stationName = None
    dfReturn.timeperiod = None
    
    # locData metadata
    dfReturn.yearID = year
    dfReturn.seasonID = season
    dfReturn.monthID = month
    dfReturn.dkID = dekadal
    
    return dfReturn