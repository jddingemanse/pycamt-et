# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 15:00:16 2022
Ideas:
    - SST: after download, save the file local. Every time first check for a local file.


@author: jandirk
"""

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt
import matplotlib.patches as _mpatches

from pycamtET.support import _dayEmpty,_dkEmpty,_monthEmpty,_dkTicks,_monthTicks,_twoMonthEmpty,_twoMonthTicks,_colorDict
from pycamtET.support import saveCheck as _saveCheck,vecAvg as _vecAvg

from pycamtET.pckgSettings import getSettings as _getSettings

#### Plot: all years
def yearBar(yeardf,savePath=None):
    """
    Create a bar chart of all yearly averages of a provided DataFrame for one station.

    Parameters
    ----------
    yeardf : Pandas DataFrame
        A yearly dataFrame that is returned by the function dFu.timedata().
    savePath : None or STR to folder. Default None.
        If None, nothing will be exported. If a string with a valid path to a folder
        is provided, the figure will be saved in the specified folder and the data
        used for the figure will be saved as a csv file in the specified folder.


    Returns
    -------
    fig : matplotlib Figure
        The created bar chart.

    """
    df=yeardf
    
    if df.timeperiod!='year':
        print('The provided dataFrame is not a yearly data dataframe.\n',
              'Please provide a single station yearly ordered dataFrame.')
        return
    
    # Getting metaData
    timeperiod = df.timeperiod
    stationName = df.stationName
    element = df.element
    unit = df.unit
    long_name = df.long_name
    
    fig,ax=_plt.subplots(figsize=(18,12))
    ax.bar(df.YEAR,df[element],color=_colorDict[element],label=long_name)
    ax.plot(df.YEAR,df[element+'avg'],c=_colorDict[element],ls=':',label='Full period average')
    ax.set_xlabel('Year',size=15)
    ax.set_ylabel(long_name+' '+unit,size=15)
    ax.set_title(stationName+' '+long_name,size=20)
    fig.legend(loc='lower center',ncol=2,fontsize=15)
    ax.grid(axis='y',ls='-',dashes=(5, 2))
    
    # Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+timeperiod+'.jpg'
        csvPath = savePath+'/'+element+stationName+timeperiod+'.csv'
        fig.savefig(figPath)
        df.to_csv(csvPath,index=False)
        print('Figure exported to %s and %s.' % (figPath,csvPath))    
    
    return fig

#### Plot: seasons all year average versus selected year
def seasonBar(seasondf,year,savePath=None):
    """
    Create a bar chart of the season averages of a selected year and all-year averages of a provided DataFrame for one station.

    Parameters
    ----------
    seasondf : Pandas DataFrame
        A seasonly dataFrame that is returned by the function dFu.timedata().
    year : integer.
        The year to be shown versus the average of all years from the provided dataFrame.
    savePath : None or STR to folder. Default None.
        If None, nothing will be exported. If a string with a valid path to a folder
        is provided, the figure will be saved in the specified folder and the data
        used for the figure will be saved as a csv file in the specified folder.

    Returns
    -------
    fig : matplotlib Figure
        The created bar chart.
    """
    df=seasondf
        
    if df.timeperiod!='season':
        print('The provided dataFrame is not a seasonly data dataframe.\n',
              'Please provide a single station seasonly ordered dataFrame.')
        return
    if (year not in df.YEAR.unique()):
        print('The chosen year is not in the provided dataframe.\n',
              'Make sure that the year is provided as integer')
        return
    # Getting metaData
    timeperiod = df.timeperiod
    stationName = df.stationName
    element = df.element
    unit = df.unit
    long_name = df.long_name
    
    subdf = df[df.YEAR==year]
    x1 = _np.linspace(0.6,2.6,3)
    x2 = _np.linspace(1.05,3.05,3)
    fig,ax=_plt.subplots(figsize=(12,12))
    ax.bar(x1,subdf[element],align='edge',width=0.35,color=_colorDict[element],label=str(year)+' '+long_name)
    ax.bar(x2,subdf[element+'avg'],align='edge',width=0.3,color=_colorDict[element],hatch='x',label='Full period average')
    ax.set_xticks(_np.linspace(1,3,3))
    ax.set_xticklabels(subdf.season)
    ax.set_xlabel('Season',size=15)
    ax.set_ylabel(long_name+' '+unit,size=15)
    ax.set_title(stationName+' '+long_name,size=20)
    fig.legend(fontsize=15,loc='lower center',ncol=3)
    
    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+timeperiod+str(year)+'.jpg'
        csvPath = savePath+'/'+element+stationName+timeperiod+'.csv'
        fig.savefig(figPath)
        df.to_csv(csvPath,index=False)
        print('Figure exported to %s and %s' % (figPath,csvPath))    
    
    return fig

#### Plot: selected year versus historic for 1 element
def recentHistoric(dataFrame,year,savePath=None):
    """
    This function creates a plot of dekadals or months from a selected year versus the average and 5-95 percentiles of the similar timeperiod averaged over all years.
    The dataFrame provided should be a dataFrame resulting from the function dFu.timedata(), with timeperiod dekadal or month.

    Parameters
    ----------
    dataFrame : Pandas DataFrame
        A dekadal or monthly dataFrame that is returned by the function dFu.timedata()
    year : integer.
        The year to be shown versus the average of all years from the provided dataFrame.
    savePath : None or STR to folder. Default None.
        If None, nothing will be exported. If a string with a valid path to a folder
        is provided, the figure will be saved in the specified folder and the data
        used for the figure will be saved as a csv file in the specified folder.

    Returns
    -------
    A collection of (DataFrame,Figure)
        DataFrame: DataFrame with the data used for the plot (historical means, percentiles and selected year means)
        Figure: the Figure created during this function.
    """        
    df = dataFrame
    stationName = df.stationName
    element = df.element
    long_name = df.long_name
    unit = df.unit
    timeperiod = df.timeperiod

    firstYear = df.YEAR.min()
    lastYear = df.YEAR.max()
    
    if timeperiod == 'dekadal':
        indexList = ['MONTH','dk']
        xticklabels = _dkTicks
        dfFull = _dkEmpty.copy()
    elif timeperiod == 'month':
        indexList = ['MONTH']
        xticklabels = _monthTicks
        dfFull = _monthEmpty.copy()
    else:
        print('Function not supported for this type of dataframe.')
        return

    dfSelect = df[df.YEAR==year].set_index(indexList).drop(columns=['YEAR'])

    grouper = df.drop(columns=['YEAR',element+'avg',element+'std','periodDays','nonaFrac']).groupby(indexList)
    dfHist = grouper.mean()
    per5 = grouper.quantile(q=0.05)
    per95 = grouper.quantile(q=0.95)
    dfHist['per5']=per5[element]
    dfHist['per95']=per95[element]
    
    dfFull=dfFull.join(dfHist.rename(columns={element:element+'hist'}))
    dfFull=dfFull.join(dfSelect.get([element]).rename(columns={element:element+'recent'}))

    labelHist = str(firstYear)+'-'+str(lastYear)
    labelSelect = str(year)

    fig,ax = _plt.subplots(figsize=(18,12))
    x = _np.arange(len(dfFull))

    color = _colorDict[element]

    ax.plot(x,dfFull[element+'recent'],c=color,label=labelSelect+' '+element)
    ax.plot(x,dfFull[element+'hist'],ls='--',c=color,label=labelHist+' '+element+' average')
    ax.fill_between(x,dfFull.per5,dfFull.per95,alpha=0.1,color=color,label=element+' 5 to 95 perc. '+labelHist)
    ax.set_ylabel(long_name+' '+unit,fontsize=15)

    ax.set_xticks(x)
    
    
    ax.set_xticklabels(xticklabels,rotation='vertical')
    ax.set_xlabel(timeperiod,fontsize=15)
    ax.grid(axis='y',ls='-',dashes=(5, 2))

    fig.legend(loc='lower center',ncol=3,fontsize=15)
    
    fig.suptitle(stationName+' '+long_name+' '+timeperiod+' average\n'+labelSelect+' versus '+labelHist,fontsize=20)
    
    # Save metadata
    dfFull.stationName = stationName
    dfFull.firstYear = firstYear
    dfFull.lastYear = lastYear
    
    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+timeperiod+'.jpg'
        csvPath = savePath+'/'+element+stationName+timeperiod+'.csv'
        fig.savefig(figPath)
        dfFull.to_csv(csvPath,index=False)
        print('Data exported to %s and %s.' % (figPath,csvPath))
    
    return dfFull,fig

def sstNoaa(years,savePath=None):
    """
    Create lineplots of Sea Surface Temperature (sst) two-year monthly anomalies, for a maximum of four two-year periods, as well as the 5-95 percentile of all available two-year periods.
    The sst data is downloaded from https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    
    Parameters
    ----------
    years : array-like, collection of years as integers
        The starting years of two-year periods to present in the plot.
        A maximum of four years can be provided.
    savePath : string, optional
        A valid folder path as string. The default is None.
        If None, data is not exported to the computer. If provided, data is exported to the provided folder.

    Returns
    -------
    fig : matplotlib Figure
        The created figure.

    """    
    localFile = _getSettings()['pckgsdataPath']+'/sstNOAA.csv'
    
    try:
        sstAnom=_pd.read_csv('https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices',delim_whitespace=True)
        print('Data downloaded. Saving to PC as '+localFile)
        sstAnom.to_csv(localFile,index=False)
    except:
        try:
            sstAnom = _pd.read_csv(localFile)
            print('Not connected to the internet, local file data/sstNOAA.csv is used.')
        except:
            print('The SST data could not be loaded. Make sure you are connected to the internet.')
            return
        
    dfsst = sstAnom.get(['YR','MON','ANOM.3']).rename(columns={'YR':'year','MON':'month','ANOM.3':'anom'})
    
    years = _np.array(years)
    
    yearsS = _pd.Series(years)
    if (~yearsS.isin(dfsst.year)).sum()>0:
        missingYears = str(years[~yearsS.isin(dfsst.year)].values)
        print('The provided years '+missingYears+' are not in the database.',
              'Please select other years')
        return
    elif len(years) > 4:
        print('You provided more than 4 years. Please select maximum 4 years')
        return
    elif (yearsS.diff()<2).sum()>0:
        print('The difference between some of the selected years is less than 2.\n',
              'Please select years with at least 2 years difference from each other.')
        return
    
    #Create the categories
    categories = []
    intList = []
    for i in range(len(years)):
        categories.append('period '+str(i))
        interval = _pd.Interval(left=years[i],right=years[i]+1,closed='both')
        intList.append(interval)
    intervalindex=_pd.IntervalIndex(intList)
    category = _pd.cut(dfsst.year,intervalindex).replace(intervalindex,categories)
    
    dfSel = dfsst[category.notna()]
    dfSel = dfSel.assign(category=category.dropna())
    
    conds = [(dfSel.year.isin(years)),dfSel.year.isin(years+1)]
    dfSel.loc[:,'relYear'] = _pd.Series(_np.select(conds,[1,2]),index=dfSel.index)
    
    dfSel = dfSel.set_index(['relYear','month'])
    
    dfTwoYear = _twoMonthEmpty.copy()
    for categ in _pd.unique(dfSel.category):
        dfTwoYear[categ] = dfSel[dfSel.category==categ].anom
       
    colorList = ['k','k','r','b']
    weightList = [3,3,3,3]
    styleList = ['--','-','-','-']
    x = _np.arange(len(dfTwoYear))
    colNames = dfTwoYear.columns[:4]
    # Get the maximum absolute value, round it to .5 and use it as ylim
    ymax = (dfTwoYear.get(colNames).abs().max().max()*2+1)//1/2
    if ymax<2: ymax=2
    ymin = -ymax

    fig,ax=_plt.subplots(figsize=(18,12))

    ax.fill_between(x,[0.5]*len(x),[ymax]*len(x),color='r',alpha=0.5)
    ax.fill_between(x,[ymin]*len(x),[-0.5]*len(x),color='b',alpha=0.5)
    
    ax.text(6,1,'El Niño',va='bottom',rotation='vertical',size=30,weight='bold')
    ax.text(6,-1,'La Niña',va='top',rotation='vertical',size=30,weight='bold')
    ax.text(23.2,0,'Neutral',va='center',rotation='vertical',size=30,weight='bold')
    
    for i in range(len(years)):
        label = str(years[i])+'-'+str(years[i]+1)
        ax.plot(x,dfTwoYear[colNames[i]],c=colorList[i],label=label,ls=styleList[i],lw=weightList[i])
        
    ax.set_ylim(ymin,ymax)
    ax.set_yticks(_np.linspace(ymin,ymax,int((ymax-ymin)*2+1)))
    ax.grid(axis='y',ls='-',dashes=(5, 2))
    
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')
    
    fig.legend(fontsize=15)
    
    ax.set_xticks(x)
    ax.set_xticklabels(_twoMonthTicks,size=15,rotation='vertical')
    ax.set_ylabel('Anomaly (\u00B0C)',size=15)
    ax.set_title('Sea surface temperature anomaly for selected years',size=20)

    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/sstAnomalies.jpg'
        csvPath = savePath+'/sstAnomalies.csv'
        fig.savefig(figPath)
        dfsst.to_csv(csvPath,index=False)
        print('Data exported to %s and %s.' % (figPath,csvPath))    

    return fig

def twoYearAnom(monthdf,years,savePath=None):
    """
    Create, for a single station, lineplots of two-year monthly anomalies, for a maximum of four two-year periods,
    as well as the 5-95 percentile of all available two-year periods.
    
    Parameters
    ----------
    monthdf : Pandas DataFrame
        A DataFrame with monthly data of a single station.
    years : array-like, collection of years as integers
        The starting years of two-year periods to present in the plot.
        A maximum of four years can be provided.
    savePath : string, optional
        A valid folder path as string. The default is None.
        If None, data is not exported to the computer. If provided, data
        is exported to the provided folder.

    Returns
    -------
    fig : matplotlib Figure
        The created figure.

    """
    df = monthdf
    stationName = df.stationName
    element = df.element
    long_name = df.long_name
    unit = df.unit
    timeperiod = df.timeperiod
    dimension = df.dimension
    
    years = _np.array(years)
    
    yearsS = _pd.Series(years)
    if (timeperiod!='month') or (dimension!='temporal'):
        print('The provided dataframe is not a single station monthly timeseries.\n',
              'Please provide another dataframe.')
    elif (~yearsS.isin(df.YEAR)).sum()>0:
        missingYears = str(years[~yearsS.isin(df.YEAR)].values)
        print('The provided years '+missingYears+' are not in the database.',
              'Please select other years')
        return
    elif len(years) > 4:
        print('You provided more than 4 years. Please select maximum 4 years')
        return
    elif (yearsS.diff()<2).sum()>0:
        print('The difference between some of the selected years is less than 2.\n',
              'Please select years with at least 2 years difference from each other.')
        return
    
    #Create anomaly
    df.loc[:,'anom'] = df[element]-df[element+'avg']
    
    #Create the categories
    categories = []
    intList = []
    for i in range(len(years)):
        categories.append('period '+str(i))
        interval = _pd.Interval(left=years[i],right=years[i]+1,closed='both')
        intList.append(interval)
    intervalindex=_pd.IntervalIndex(intList)
    category = _pd.cut(df.YEAR,intervalindex).replace(intervalindex,categories)
    
    dfSel = df[category.notna()]
    dfSel = dfSel.assign(category=category.dropna())
    
    conds = [(dfSel.YEAR.isin(years)),dfSel.YEAR.isin(years+1)]
    dfSel.loc[:,'relYear'] = _pd.Series(_np.select(conds,[1,2]),index=dfSel.index)
        
    dfSel = dfSel.set_index(['relYear','MONTH'])
    
    dfTwoYear = _twoMonthEmpty.copy()
    for categ in _pd.unique(dfSel.category):
        dfTwoYear.loc[:,categ] = dfSel[dfSel.category==categ]['anom']
    
    # Add percentiles of all two-year periods (year 1: all even years. Year 2: all uneven years)
    per5 = df.get(['MONTH','anom']).groupby(by=[df.YEAR%2+1,'MONTH']).quantile(0.05)
    per95 = df.get(['MONTH','anom']).groupby(by=[df.YEAR%2+1,'MONTH']).quantile(0.95)
    dfTwoYear.loc[:,'per5'] = per5
    dfTwoYear.loc[:,'per95'] = per95
    
    colorList = ['r','g','b','k']
    weightList = [3,3,3,3]
    styleList = ['--',':','-.','-']
    x = _np.arange(len(dfTwoYear))
    colNames = dfTwoYear.columns[:-2]
    fig,ax=_plt.subplots(figsize=(18,12))
    
    for i in range(len(colNames)):
        label = str(years[i])+'-'+str(years[i]+1)
        ax.plot(x,dfTwoYear[colNames[i]],c=colorList[i],label=label,ls=styleList[i],lw=weightList[i])
    ax.fill_between(x,dfTwoYear.per5,dfTwoYear.per95,color='k',alpha=0.05,label='5-95 perc.\naverages')
    
    fig.legend(fontsize=15)
    
    ax.set_xticks(x)
    ax.set_xticklabels(_twoMonthTicks,size=15,rotation='vertical')
    ax.set_ylabel('Anomaly '+unit,size=15)
    ax.set_title(stationName+' '+long_name+' anomaly for selected years',size=20)
    ax.grid(axis='y',ls='-',dashes=(5, 2))

    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+'2yearAnomalies.jpg'
        csvPath = savePath+'/'+element+stationName+'2yearAnomalies.jpg'
        fig.savefig(figPath)
        dfTwoYear.to_csv(csvPath,index=False)
        print('Data exported to %s and %s.' % (figPath,csvPath))    

    return fig

def yearAnom(yeardf,savePath=None):
    """
    Create a bar chart of yearly anomalies (yearly average - full average), for a single station.

    Parameters
    ----------
    yeardf : Pandas DataFrame
        A DataFrame with yearly data of a single station.
    savePath : string, optional
        A valid folder path as string. The default is None.
        If None, data is not exported to the computer. If provided, data is exported to the provided folder.

    Returns
    -------
    fig : matplotlib Figure
        The created bar chart.

    """
    # dataFrame input: yearT
        
    df = yeardf
    stationName = df.stationName
    element = df.element
    long_name = df.long_name
    unit = df.unit
    timeperiod = df.timeperiod
    dimension = df.dimension
        
    if (timeperiod!='year') or (dimension!='temporal'):
        print('The provided dataframe is not a single station yearly timeseries.\n',
              'Please provide another dataframe.')
        return
    
    df.loc[:,'anom'] = df[element] - df[element+'avg']    
    
    if (element == 'PRECIP') or (element == 'RD'):
        colorList = ['r','g']
    elif (element == 'TMPMIN') or (element == 'TMPMAX'):
        colorList = ['b','r']
    
    fig,ax=_plt.subplots(figsize=(18,12))
    ax.bar(df.YEAR[df['anom']<=0],df['anom'][df['anom']<=0],color=colorList[0])
    ax.bar(df.YEAR[df['anom']>0],df['anom'][df['anom']>0],color=colorList[1])
    ax.set_xlabel('Year',size=15)
    ax.set_ylabel('Anomaly '+unit,size=15)
    ax.set_title(stationName+' '+long_name+' anomaly',size=20)
    ax.grid(axis='y',ls='-',dashes=(5, 2))

    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+'YearAnom.jpg'
        csvPath = savePath+'/'+element+stationName+'YearAnom.csv'
        fig.savefig(figPath)
        df.to_csv(csvPath)
        print('Data exported to %s and %s.' % (figPath,savePath))    
        
    return fig

def cumulativeRF(dekadf,year,season=None,savePath=None):
    df = dekadf
    stationName = df.stationName
    element = df.element
    long_name = df.long_name
    unit = df.unit
    timeperiod = df.timeperiod
    dimension = df.dimension
        
    if (timeperiod!='dekadal') or (dimension!='temporal') or (element!='PRECIP'):
        print('The provided dataframe is not a single station dekadal PRECIP timeseries.\n',
              'Please provide another dataframe.')
        return
    
    if year not in df.YEAR.values:
        print('The provided year is not in the provided dataframe. Please select another year or provide another dataframe.')
        return
    if season!=None:
        if season not in ['Bega','Belg','Kiremt']:
            print('Season not recognized. Please select one of Bega, Belg, Kiremt.')
            return
        else:
            df = dekadf.copy()
            df.loc[df.MONTH==1,'YEAR'] = df.YEAR[df.MONTH==1]-1
            if season=='Bega':
                seasonlist = [1,10,11,12]
            elif season == 'Belg':
                seasonlist = [2,3,4,5]
            else:
                seasonlist = [6,7,8,9]    
    else: #situation: only year provided
        seasonlist = [1,2,3,4,5,6,7,8,9,10,11,12]
    
    dfCumAll = df.get(['YEAR','MONTH','dk','PRECIP','PRECIPavg'])[df.MONTH.isin(seasonlist)]
    dfCumAll = dfCumAll.groupby(by=['YEAR','MONTH','dk']).mean().reset_index()
    dfCumAll.PRECIP.fillna(value=0,inplace=True) #fill missing values with 0 before taking cumulative, in order not to have missing cumulative values ###solution needed: make sure for every year there are all months
    dfCumAll['cumulative'] = dfCumAll.get(['YEAR','PRECIP']).groupby(by=['YEAR']).cumsum()['PRECIP'].values
    per5cum = dfCumAll.groupby(by=['MONTH','dk']).quantile(0.05)['cumulative']
    per95cum  = dfCumAll.groupby(by=['MONTH','dk']).quantile(0.95)['cumulative']
    avgcum  = dfCumAll.groupby(by=['MONTH','dk']).mean()['cumulative']
    dfCum = _dkEmpty.copy()
    dfCum['cumulative'] = dfCumAll[dfCumAll.YEAR==year].set_index(['MONTH','dk'])['cumulative']
    dfCum['avgcum'] = avgcum
    dfCum['per5cum'] = per5cum
    dfCum['per95cum'] = per95cum
    
    dkTicksSeason = _dkTicks[dfCum.cumulative.notna().values] ##Problem for example Assela 2015 PRECIP, because that year has missing data. This should only drop the ticks not belonging to the season. Only temporary fix, with the if.
    dfCum = dfCum.dropna(how='all')
    
    if season == 'Bega':
        dfCum = dfCum.iloc[-9:].append(dfCum.iloc[:3])
        dkTicksSeason = dkTicksSeason.iloc[-9:].append(dkTicksSeason.iloc[:3])
    
    fig,ax=_plt.subplots(figsize=(18,12))
    
    x = _np.arange(len(dfCum))
    ax.plot(x,dfCum['cumulative'],'k',label='cumulative '+str(year))
    ax.plot(x,dfCum['avgcum'],'--k',label='cumulative all years')
    ax.fill_between(x,dfCum['per5cum'],dfCum['per95cum'],alpha=0.1,color='k',label='5-95 percentile')
    ax.set_title(stationName+' rainfall, cumulative\n'+str(year)+' versus all years',fontsize=20)
    ax.set_ylabel('Sum of rainfall (mm)',fontsize=15)
    ax.set_xlabel('Dekadal',fontsize=15)
    ax.set_xticks(x)
    ax.set_xticklabels(dkTicksSeason,size=15,rotation='vertical')
    ax.grid(axis='y',ls='-',dashes=(5, 2))
    
    fig.legend(fontsize=15)

    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']    
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+str(year)+'cumulative.jpg'
        csvPath = savePath+'/'+element+stationName+str(year)+'cumulative.csv'
        fig.savefig(figPath)
        dfCum.to_csv(csvPath,index=False)
        print('Data exported to %s and %s.' % (figPath,csvPath))
    
    return dfCum,fig

def cumulativeRFday(daydf,year,season=None,savePath=None):
    df = daydf
    stationName = df.stationName
    element = 'PRECIP'
    long_name = 'precipitation'
    unit = ' (mm)'
    # timeperiod = df.timeperiod
    # dimension = df.dimension
        
    if ('PRECIP' not in df.columns):
        print('The provided dataframe does not have PRECIP data.\n',
              'Please provide another dataframe.')
        return
    
    if year not in df.YEAR.values:
        print('The provided year is not in the provided dataframe. Please select another year or provide another dataframe.')
        return
    if season!=None:
        if season not in ['Bega','Belg','Kiremt']:
            print('Season not recognized. Please select one of Bega, Belg, Kiremt.')
            return
        else:
            df = daydf.copy()
            df.loc[:,'YEAR']=df.seasonyear
            if season=='Bega':
                seasonlist = [1,10,11,12]
            elif season == 'Belg':
                seasonlist = [2,3,4,5]
            else:
                seasonlist = [6,7,8,9]  
            timeStr = str(year)+' '+season
    else: #situation: only year provided
        seasonlist = [1,2,3,4,5,6,7,8,9,10,11,12]
        timeStr = str(year)
    
    dfCumAll = df.get(['YEAR','MONTH','day','PRECIP'])[df.MONTH.isin(seasonlist)]
    dfCumAll = dfCumAll.groupby(by=['YEAR','MONTH','day']).mean().reset_index()
    dfCumAll.PRECIP.fillna(value=0,inplace=True) #fill missing values with 0 before taking cumulative, in order not to have missing cumulative values
    dfCumAll['cumulative'] = dfCumAll.get(['YEAR','PRECIP']).groupby(by=['YEAR']).cumsum()['PRECIP'].values
    per5cum = dfCumAll.groupby(by=['MONTH','day']).quantile(0.05)['cumulative']
    per95cum  = dfCumAll.groupby(by=['MONTH','day']).quantile(0.95)['cumulative']
    avgcum  = dfCumAll.groupby(by=['MONTH','day']).mean()['cumulative']
    dfCum = _dayEmpty.copy()
    dfCum['cumulative'] = dfCumAll[dfCumAll.YEAR==year].set_index(['MONTH','day'])['cumulative']
    dfCum['avgcum'] = avgcum
    dfCum['per5cum'] = per5cum
    dfCum['per95cum'] = per95cum
    
    dfCum = dfCum.dropna(how='all')
    
    if season == 'Bega':
        dfCum = dfCum.iloc[31:].append(dfCum.iloc[:31])
        #dkTicksSeason = dkTicksSeason.iloc[-9:].append(dkTicksSeason.iloc[:3])
    
    # Create ticks
    ticklist = []
    ticklabellist = []
    dfCum2 = dfCum.reset_index()
    for i in seasonlist:
        idxmin = dfCum2.MONTH[dfCum2.MONTH==i].idxmin()
        ticklist.append(idxmin)
        ticklabellist.append(_monthTicks[i-1]+' 1')
    
    fig,ax=_plt.subplots(figsize=(18,12))
    
    x = _np.arange(len(dfCum))
    ax.plot(x,dfCum['cumulative'],'k',label='cumulative '+str(year))
    ax.plot(x,dfCum['avgcum'],'--k',label='cumulative all years')
    ax.fill_between(x,dfCum['per5cum'],dfCum['per95cum'],alpha=0.1,color='k',label='5-95 percentile')
    ax.set_title(stationName+' rainfall, cumulative\n'+timeStr+' versus all years',fontsize=20)
    ax.set_ylabel('Sum of rainfall (mm)',fontsize=15)
    ax.set_xlabel('Month',fontsize=15)
    ax.set_xticks(ticklist)
    ax.set_xticklabels(ticklabellist,size=15)
    ax.grid(axis='y',ls='-',dashes=(5, 2))
    
    fig.legend(fontsize=15)

    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']    
    if _saveCheck(savePath):
        figPath = savePath+'/'+element+stationName+str(year)+'cumulative.jpg'
        csvPath = savePath+'/'+element+stationName+str(year)+'cumulative.csv'
        fig.savefig(figPath)
        dfCum.to_csv(csvPath,index=False)
        print('Data exported to %s and %s.' % (figPath,csvPath))
    
    return dfCum,fig

def windRose(df,stationName,year,season=None,month=None,savePath=None):
    """
    df should be a DataFrame with columns STN_Name, dateTime, WINSPD and WINDIR
    """
    
    if month!=None:
        winddf = df[(df.STN_Name==stationName)&(df.dateTime.dt.year==year)&(df.dateTime.dt.month==month)]
        timeStr = str(year)+' '+str(month)
        if (year not in winddf.dateTime.dt.year.values) or (month not in winddf.dateTime.dt.month.values):
            print('Chosen year or month is not available. Please select another year')
            return
    elif season!=None:
        winddf = df[(df.STN_Name==stationName)&(df.seasonyear==year)&(df.season==season)]
        timeStr = str(year)+' '+season
    else:
        
        winddf = df[(df.STN_Name==stationName)&(df.dateTime.dt.year==year)]
        if year not in winddf.dateTime.dt.year.values:
            print('Chosen year is not available. Please select another year')
            return
        timeStr = str(year)
    
    
    wind_na = len(winddf)-len(winddf.dropna())
    wind_na_per = round(wind_na*100/len(winddf),1)
    wind_zero = len(winddf[winddf.WINDIR==0])
    wind_zero_per = round(wind_zero*100/len(winddf),1)
    wind_zero_str = str(wind_zero)+' values ('+str(round(wind_zero*100/len(winddf),1))+'%) zero.'
    windPlotDf = winddf[winddf.WINDIR!=0].dropna()
    percor = len(windPlotDf)/len(winddf)
    
    from windrose import WindroseAxes
    ax = WindroseAxes.from_ax()
    colors = ['midnightblue','royalblue','cyan','greenyellow','orange','maroon']
    ax.bar(windPlotDf.WINDIR, windPlotDf.WINSPD,opening=0.8,bins=6,colors=colors, edgecolor='white',normed=True) ##Normed is true: probably count of values, with normed leading to total count 100.
    yticks = ax.get_yticks() * percor #show percentages including the zero values
    yticklabels = []
    for ytick in yticks:
        yticklabel = str(_np.round(ytick,1))+'%'
        yticklabels.append(yticklabel)
    ax.set_yticklabels(yticklabels)

    ax.set_title(timeStr+' '+stationName)

    #produce legend
    patch1 = _mpatches.Patch(edgecolor='white',facecolor='white', label='%s%% calms\n%s%% missing' %(wind_zero_per,wind_na_per))
    patches = [patch1]
    bins = _np.round(ax._info['bins'],1)
    for i,color in enumerate(colors):
        label = '['+str(bins[i])+'-'+str(bins[i+1])+')'
        if i == len(colors)-1:
            label = '>= '+str(bins[i])
        patch = _mpatches.Patch(edgecolor='k',facecolor=color, label=label)
        patches.append(patch)
    fig = _plt.gcf()
    fig.legend(handles=patches,loc='lower left')
    
    ws_avg,wdir_avg = _vecAvg(winddf.WINSPD,winddf.WINDIR)
    
    print('Windrose created for %s at station %s.\n' % (timeStr,stationName),
          'For this period, average windspeed is %s m/s, and average winddirection is %s\u00B0.' % (ws_avg,wdir_avg),
          'During this period, %s%% are calms and %s%% are missing.' %(wind_zero_per,wind_na_per))
    
    #Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']    
    if _saveCheck(savePath):
        figPath = savePath+'/'+stationName+timeStr+'windrose.jpg'
        fig.savefig(figPath)
        print('Data exported to %s.' % (figPath))
    
    return fig