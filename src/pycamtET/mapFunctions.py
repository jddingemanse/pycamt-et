# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 20:28:32 2022
    -check the indexing of _np.meshgrid!
    -check minimmum temp idw error

@author: jandirk
"""
#### Import libraries
import numpy as _np
import matplotlib.pyplot as _plt
from matplotlib import cm as _cm
import pandas as _pd

from pycamtET.support import saveCheck as _saveCheck
from pycamtET.supportMap import _metercrs,_adm_d,_adm2_d,_adm1_d,_adm0_d,_legend_elements
from pycamtET.supportMap import gridcalculate as _gridcalculate

from pycamtET.pckgSettings import getSettings as _getSettings
_siPath = _getSettings()['pckgsdataPath']+'\\stationinfo.csv'

def kriMap(dfLoc,region=None,adm2=None,adm3=None,krigingModel='gaussian',savePath=None):
    """
    Based on provided locations and their info, create a map based on Kriging.
    On a rectangle grid of 100 * 100 points covering the full region, the estimated value is calculated with OrdinaryKriging from the package pykrige.
    After that, the points within the polygon of the region are kept.
    Two maps are created: the absolute values, and the anomaly.
    Anomalies for temperature data: observation - average.
    Anomaly for rainfall data: in categories under<75%<=normal<125%<over for <75%<125%<

    Parameters
    ----------
    dfLoc : Pandas DataFrame
        A dataFrame returned by the function dFu.locData(), holding data of an element for a certain timeperiod for multiple stations.
    krigingModel : str
        Used as input for pykrige.ok.OrdinaryKriging(variogram_model).
        Specifies which variogram model to use; may be one of the following:
        linear, power, gaussian, spherical, exponential, hole-effect.
    savePath : string, optional
        A valid folder path as string. The default is None.
        If None, data is not exported to the computer. If provided, data is exported to the provided folder.

    Returns
    -------
    (fig1,fig2) : matplotlib Figures
        The created absolute and anomaly maps.

    """        
    # Retrieve metadata
    dekadal = dfLoc.dkID    
    month = dfLoc.monthID
    season = dfLoc.seasonID
    year = dfLoc.yearID
    element = dfLoc.element
    long_name = dfLoc.long_name
    unit = dfLoc.unit
    
    timeStr = str(year)
    if season != None:
        timeStr += ' '+season
    if month != None:
        timeStr += ' '+str(month)
    if dekadal != None:
        timeStr += ' dk'+str(dekadal)

    stationInfo = _pd.read_csv(_siPath)
    df = dfLoc.join(stationInfo.set_index(['STN_Name'])).drop_duplicates(subset=['GEOGR1','GEOGR2'])

    # get the shapefile corresponding to the selected area
    if (adm3!=None):
        if (adm3 not in _adm_d.admin3Name.values):
            print('The selected adm3 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm_d[_adm_d.admin3Name==adm3]
            plotshape = _adm_d[_adm_d.admin3Name==adm3]
            areaname = adm3
    elif (adm2!=None):
        if (adm2 not in _adm2_d.admin2Name.values):
            print('The selected adm2 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm2_d[_adm2_d.admin2Name==adm2]
            plotshape = _adm_d[_adm_d.admin2Name==adm2]
            areaname = adm2
    elif (region!=None):
        if (region not in _adm_d.admin1Name.values):
            print('The selected adm3 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm1_d[_adm1_d.admin1Name==region]
            plotshape = _adm2_d[_adm2_d.admin1Name==region]
            areaname = region
    else:
        gpdshape = _adm0_d
        plotshape = _adm1_d
        areaname = 'Ethiopia'

    # Prepare grid data
    gridinfo = _gridcalculate(gpdshape,areaname)
    gridx = gridinfo.x_d.unique()
    gridy = gridinfo.y_d.unique()
    bool2d = _np.array(gridinfo.bool1d).reshape(gridx.size,gridy.size)

    nona = df[element].notna()
    x = df.GEOGR1[nona]
    y = df.GEOGR2[nona]
    z = df[element][nona]
    zavg = df[element+'avg'][nona]

    from pykrige.ok import OrdinaryKriging
    
    OK = OrdinaryKriging(x,y,z,variogram_model=krigingModel,verbose=False,enable_plotting=False)
    OKavg = OrdinaryKriging(x,y,zavg,variogram_model=krigingModel,verbose=False,enable_plotting=False)
    zgrid,ss = OK.execute('grid',gridx,gridy)
    zgridavg,ssavg = OKavg.execute('grid',gridx,gridy)
    
    zgrid[~bool2d] = _np.nan
    zgridavg[~bool2d] = _np.nan

    if (element == 'PRECIP') or (element == 'RD'):
        zgridanom = zgrid/zgridavg
        cmap = 'RdYlGn'
    elif (element == 'TMPMIN') or (element =='TMPMAX'):
        zgridanom = zgrid-zgridavg
        cmap = 'coolwarm'
    else:
        print('Element not yet supported.')
        return
    
    fig1,ax1=_plt.subplots()
    fig2,ax2=_plt.subplots()
    ax1.contourf(gridx,gridy,zgrid,cmap=cmap)
    cbar = fig1.colorbar(_cm.ScalarMappable(cmap=cmap),location='bottom')
    cbar.set_ticks(_np.linspace(0,1,5))
    cbar.set_ticklabels(_np.round(_np.linspace(_np.nanmin(zgrid),_np.nanmax(zgrid),5),0))
    cbar.set_label(element+' '+unit)    

    if (element == 'PRECIP') or (element == 'RD'):
        ax2.contourf(gridx,gridy,zgridanom,levels=[0,0.75,1.25,100],colors=['r','yellow','green'])
        fig2.legend(handles=_legend_elements,loc='lower center',ncol=3)
    elif (element == 'TMPMIN') or (element =='TMPMAX'):
        absmax = _np.max(_np.abs((_np.nanmin(zgridanom),_np.nanmax(zgridanom))))
        ax2.contourf(gridx,gridy,zgridanom,cmap=cmap,vmin=-absmax,vmax=absmax)
        cbar2 = fig2.colorbar(_cm.ScalarMappable(cmap=cmap),location='bottom')
        cbar2.set_ticks(_np.linspace(0,1,5))
        cbar2.set_ticklabels(_np.round(_np.linspace(-absmax,absmax,5),1))
        cbar2.set_label(element+' anomaly '+unit)          
    
    ax1.set_title(long_name+' kriging\n'+timeStr+' '+areaname)
    ax2.set_title(long_name+' kriging anomaly\n'+timeStr+' '+areaname)
    
    plotshape.plot(ax=ax1,facecolor='none')
    plotshape.plot(ax=ax2,facecolor='none')

    if savePath == 'default':
        savePath = _getSettings()['outPath']
    
    if _saveCheck(savePath):
        fig1Path = savePath+'/krigingAbsolute'+element+timeStr+areaname+'.jpg'
        fig2Path = savePath+'/krigingAnomaly'+element+timeStr+areaname+'.jpg'
        csvPath = savePath+'/'+element+timeStr+areaname+'stations.csv'
        fig1.savefig(fig1Path)
        fig2.savefig(fig2Path)
        df.to_csv(csvPath)
        print('Data exported to %s, %s and %s.' % (fig1Path,fig2Path,csvPath))
        
    return fig1,fig2

def idwMap(dfLoc,region=None,adm2=None,adm3=None,savePath=None):
    """
    Based on provided locations and their info, create a map based on Inverse Distance Weighting (idw).
    On a rectangle grid of 100 * 100 points covering the full region, the estimated value is calculated based on idw with all supplied station data.
    After that, the points within the polygon of the region are kept.
    Two maps are created: the absolute values, and the anomaly.
    Anomalies for temperature data: observation - average.
    Anomaly for rainfall data: in categories under<75%<=normal<125%<over for <75%<125%<

    Parameters
    ----------
    dfLoc : Pandas DataFrame
        A dataFrame returned by the function dFu.locData(), holding data of an element for a certain timeperiod for multiple stations.
    savePath : string, optional
        A valid folder path as string. The default is None.
        If None, data is not exported to the computer. If provided, data is exported to the provided folder.

    Returns
    -------
    (fig1,fig2) : matplotlib Figures
        The created absolute and anomaly maps.

    """
    # Collect metaData
    dekadal = dfLoc.dkID    
    month = dfLoc.monthID
    season = dfLoc.seasonID
    year = dfLoc.yearID
    element = dfLoc.element
    long_name = dfLoc.long_name
    unit = dfLoc.unit
    
    timeStr = str(year)
    if season != None:
        timeStr += ' '+season
    if month != None:
        timeStr += ' '+str(month)
    if dekadal != None:
        timeStr += ' dk'+str(dekadal)
    
    stationInfo = _pd.read_csv(_siPath)
    df = dfLoc.join(stationInfo.set_index(['STN_Name'])).drop_duplicates(subset=['GEOGR1','GEOGR2'])

    # get the shapefile corresponding to the selected area
    if (adm3!=None):
        if (adm3 not in _adm_d.admin3Name.values):
            print('The selected adm3 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm_d[_adm_d.admin3Name==adm3]
            plotshape = _adm_d[_adm_d.admin3Name==adm3]
            areaname = adm3
    elif (adm2!=None):
        if (adm2 not in _adm2_d.admin2Name.values):
            print('The selected adm2 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm2_d[_adm2_d.admin2Name==adm2]
            plotshape = _adm_d[_adm_d.admin2Name==adm2]
            areaname = adm2
    elif (region!=None):
        if (region not in _adm_d.admin1Name.values):
            print('The selected adm3 name is not available. Please select another name.')
            return
        else:
            gpdshape = _adm1_d[_adm1_d.admin1Name==region]
            plotshape = _adm2_d[_adm2_d.admin1Name==region]
            areaname = region
    else:
        gpdshape = _adm0_d
        plotshape = _adm1_d
        areaname = 'Ethiopia'

    # Prepare grid data
    gridinfo = _gridcalculate(gpdshape,areaname)
    gridshape = (len(gridinfo.x_d.unique()),len(gridinfo.y_d.unique()))
    bool1d = gridinfo.bool1d
    x_m = gridinfo.x_m
    y_m = gridinfo.y_m
    x2d_d = _np.array(gridinfo.x_d).reshape(gridshape)
    y2d_d = _np.array(gridinfo.y_d).reshape(gridshape)
    
    # Station lots and lans need to be turned into meter, in order to calculate distances
    import geopandas as gpd
    statpoints = gpd.points_from_xy(df.GEOGR1,df.GEOGR2,crs='epsg:4326').to_crs(_metercrs)
    stationxy = []
    for i in range(len(statpoints)):
        xypoint = _np.array((statpoints[i].x,statpoints[i].y))
        stationxy.append(xypoint)
    stationxy = _np.array(stationxy)

    estimateList = []
    estimateavgList = []
    for i in range(len(bool1d)):
        if bool1d[i]:
            gridpointxy = _np.array((x_m[i],y_m[i]))
            distances = _np.linalg.norm(gridpointxy-stationxy,axis=1)
            distInv = 1/distances
            weights = distInv/distInv.sum()
            estimates = df[element].values*weights
            estimatesavg = df[element+'avg'].values*weights
            estimate = estimates.sum()
            estimateavg = estimatesavg.sum()
        else:
            estimate = _np.nan
            estimateavg = _np.nan
        estimateList.append(estimate)
        estimateavgList.append(estimateavg)

    estimate2d = _np.array(estimateList).reshape(gridshape)
    estimateavg2d = _np.array(estimateavgList).reshape(gridshape)
    if (element == 'PRECIP') or (element == 'RD'):
        estimateanom2d = estimate2d/estimateavg2d
        cmap = 'RdYlGn'
    elif (element == 'TMPMIN') or (element =='TMPMAX'):
        estimateanom2d = estimate2d-estimateavg2d
        cmap = 'coolwarm'
    else:
        print('Element not yet supported.')
        return

    fig1,ax1=_plt.subplots()
    fig2,ax2=_plt.subplots()
    ax1.contourf(x2d_d,y2d_d,estimate2d,cmap=cmap)
    clines = ax1.contour(x2d_d,y2d_d,estimate2d,cmap=cmap)
    ax1.clabel(clines)
    cbar = fig1.colorbar(_cm.ScalarMappable(cmap=cmap),location='bottom')
    cbar.set_ticks(_np.linspace(0,1,5))
    cbar.set_ticklabels(_np.round(_np.linspace(_np.nanmin(estimate2d),_np.nanmax(estimate2d),5),0))
    cbar.set_label(element+' '+unit)
    
    if (element == 'PRECIP') or (element == 'RD'):
        ax2.contourf(x2d_d,y2d_d,estimateanom2d,levels=[0,0.75,1.25,100],colors=['r','yellow','green'])
        fig2.legend(handles=_legend_elements,loc='lower center',ncol=3)
    elif (element == 'TMPMIN') or (element =='TMPMAX'):
        absmax = _np.max(_np.abs((_np.nanmin(estimateanom2d),_np.nanmax(estimateanom2d))))
        ax2.contourf(x2d_d,y2d_d,estimateanom2d,cmap=cmap,vmin=-absmax,vmax=absmax)
        cbar2 = fig2.colorbar(_cm.ScalarMappable(cmap=cmap),location='bottom')
        cbar2.set_ticks(_np.linspace(0,1,5))
        cbar2.set_ticklabels(_np.round(_np.linspace(-absmax,absmax,5),1))
        cbar2.set_label(element+' anomaly '+unit)        
    
    ax1.set_title(long_name+' IDW\n'+timeStr+' '+areaname)
    ax2.set_title(long_name+' IDW anomaly\n'+timeStr+' '+areaname)
      
    plotshape.plot(ax=ax1,facecolor='none')
    plotshape.plot(ax=ax2,facecolor='none')
    
    # Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        fig1Path = savePath+'/idwAbsolute'+element+timeStr+areaname+'.jpg'
        fig2Path = savePath+'/idwAnomaly'+element+timeStr+areaname+'.jpg'
        csvPath = savePath+'/'+element+timeStr+areaname+'stations.csv'
        fig1.savefig(fig1Path)
        fig2.savefig(fig2Path)
        df.to_csv(csvPath)
        print('Data exported to %s, %s and %s.' % (fig1Path,fig2Path,csvPath)) 
    
    return fig1,fig2

def stationDistr(dfLoc,savePath=None):
    """

    """        
    # Retrieve metadata
    dekadal = dfLoc.dkID    
    month = dfLoc.monthID
    season = dfLoc.seasonID
    year = dfLoc.yearID
    element = dfLoc.element
    long_name = dfLoc.long_name
    unit = dfLoc.unit
    
    timeStr = str(year)
    if season != None:
        timeStr += ' '+season
    if month != None:
        timeStr += ' '+str(month)
    if dekadal != None:
        timeStr += ' dk'+str(dekadal)

    stationInfo = _pd.read_csv(_siPath)
    df = dfLoc.join(stationInfo.set_index(['STN_Name'])).drop_duplicates(subset=['GEOGR1','GEOGR2'])

    nona = df[element].notna()
    x = df.GEOGR1[nona]
    y = df.GEOGR2[nona]

    fig,ax=_plt.subplots()
    ax.scatter(x,y,c='r',label='Stations',s=5)
    _adm1_d.plot(ax=ax,facecolor='none')
    ax.set_title('Stations with data for '+element+' in the period '+timeStr)
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    ax.legend()

    # Export data
    if savePath == 'default':
        savePath = _getSettings()['outPath']
    if _saveCheck(savePath):
        figPath = savePath+'/stationDistr'+element+timeStr+'.jpg'
        fig.savefig(figPath)
        print('Data exported to %s.' % figPath) 
    
    return fig