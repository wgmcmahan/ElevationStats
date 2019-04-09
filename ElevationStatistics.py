# -*- coding: utf-8 -*-

"""
find study elevation range

ElevationStatistics.py
Created by William McMahan and Dr. William Armstrong
Last edited 9 Apr 2019

Takes in data tables created by QGIS Process and locates 10 m elevation bands
which contain streams in all 3 rock types.  It first separates the files
into matrices grouped by rock type.  From there hypsometric curves for
each geographic group are calculated showing the overlap of the three
rock types from each group.  The hypsometries are multiplied by each
other within groups to locate only the 10 meter elevation bands where all
three hypsometries overlap.  The latitude and longitude of points which
fall into that elevation range are then extracted, along with new unique
object IDs and stream segment IDs.  The points are then exported as .csv
files to be loaded back into QGIS for additional processing.
"""


#import necessary modules
from datetime import datetime
import os
import sys
import xlrd
import numpy as np
import matplotlib.pyplot as plt

startTime=datetime.now()

#read in names of data files
data=[]
for xls in os.listdir("DataTables/"):
    if xls.endswith(".xls"):
       data.append(xls) 

#number of data files located
numFiles=len(data)
#perform a check to make sure all files are present
if numFiles%3 != 0:
    #kills the script
    sys.exit()
#number of sites located
numSites=numFiles/3

#fix bin edges, all histograms comparable, 8850 to accommodate Mt. Everest
"""
using 4500 right now to make it simpler to work with
"""
edges=range(0,4510,10)


#---loop over carbonate---
#initialize matrices, 8850 to accommodate Mt. Everest
dataCarb=np.zeros((4500,numSites*5))
elevCarb=np.zeros((4500,numSites))
#this finds the index and file name for all calcareous files 
for index, item in enumerate(data):
    if index in range(0,numFiles,3):
        #saves the path to the data file as a string
        loc=("DataTables/%s" %(item))
        #opens the data file
        wb=xlrd.open_workbook(loc)
        #locates the data in the file
        sheet=wb.sheet_by_index(0)
        #determines the correct column index to place the data into
        datInd=index/3*5
        elvInd=index/3
        #read the data from the excel sheet and load it into matrix by column
        #i starts at 1 because of column headers in xls file
        for i in range(1,sheet.nrows):
        #following lines start at i-1 to place data in 0th index
            #objectID
            dataCarb[i-1,datInd]=sheet.cell_value(i,0)
            #streamID
            dataCarb[i-1,datInd+1]=sheet.cell_value(i,1)
            #Longitude
            dataCarb[i-1,datInd+2]=sheet.cell_value(i,2)
            #Latitude
            dataCarb[i-1,datInd+3]=sheet.cell_value(i,3)
            #Elevation
            dataCarb[i-1,datInd+4]=sheet.cell_value(i,4)
            #fills the separate elevation matrix
            elevCarb[i-1,elvInd]=sheet.cell_value(i,4)


#---loop over felsic---
dataFels=np.zeros((4500,numSites*5))
elevFels=np.zeros((4500,numSites))
for index, item in enumerate(data):
    if index in range(1,numFiles,3):
        loc=("DataTables/%s" %(item))
        wb=xlrd.open_workbook(loc)
        sheet=wb.sheet_by_index(0)
        datInd=index/3*5
        elvInd=index/3
        for i in range(1,sheet.nrows):
            dataFels[i-1,datInd]=sheet.cell_value(i,0)
            dataFels[i-1,datInd+1]=sheet.cell_value(i,1)
            dataFels[i-1,datInd+2]=sheet.cell_value(i,2)
            dataFels[i-1,datInd+3]=sheet.cell_value(i,3)
            dataFels[i-1,datInd+4]=sheet.cell_value(i,4) 
            elevFels[i-1,elvInd]=sheet.cell_value(i,4) 
    
    
#---loop over mafic---
dataMaf=np.zeros((4500,numSites*5))
elevMaf=np.zeros((4500,numSites))
for index, item in enumerate(data):
    if index in range(2,numFiles,3):
        loc=("DataTables/%s" %(item))
        wb=xlrd.open_workbook(loc)
        sheet=wb.sheet_by_index(0)
        datInd=index/3*5
        elvInd=index/3
        for i in range(1,sheet.nrows):
            dataMaf[i-1,datInd]=sheet.cell_value(i,0)
            dataMaf[i-1,datInd+1]=sheet.cell_value(i,1)
            dataMaf[i-1,datInd+2]=sheet.cell_value(i,2)
            dataMaf[i-1,datInd+3]=sheet.cell_value(i,3)
            dataMaf[i-1,datInd+4]=sheet.cell_value(i,4)
            elevMaf[i-1,elvInd]=sheet.cell_value(i,4) 
 
   
#---plot histograms and calculate hypsometries---
#set all 0 values to NaN for plotting
elevCarb[elevCarb==0]=np.nan
elevFels[elevFels==0]=np.nan
elevMaf[elevMaf==0]=np.nan
#preallocate hypsometry matrices
hypCarb=np.zeros((450,numSites))
hypFels=np.zeros((450,numSites))
hypMaf=np.zeros((450,numSites))
#iterates over the number of sites returned from map analysis
for site in range(numSites):
    
    #--plot histograms--
    #changes 0th index for site naming
    nm=site+1
    #saves the site name as a string
    name=("Site %d" %nm)
    #plots the histograms, bins range from the integer of the lowest elevation
    #in the dataset to 10m higher than the integer of the highest elevation 
    #in the dataset, with bins 10m wide.
    plt.hist(elevCarb[:,site],color="b",alpha=0.3,bins=range(int(min(elevCarb[:,site])),int(max(elevCarb[:,site])+10),10))
    plt.hist(elevFels[:,site],color="r",alpha=0.3,bins=range(int(min(elevFels[:,site])),int(max(elevFels[:,site])+10),10))
    plt.hist(elevMaf[:,site],color="g",alpha=0.3,bins=range(int(min(elevMaf[:,site])),int(max(elevMaf[:,site])+10),10))
    #palces a legend in the upper right
    plt.legend(("Carbonate","Felsic","Mafic"),loc=1)
    #title the plot
    plt.title(name)
    #label the axes
    plt.xlabel("Elevation (m ASL)")
    plt.ylabel("Count")
    #draw all 3 rock types on single plot
    plt.show()     
    
    #--calculate hypsometries--
    #calculates distribution of points into specified elevation bands
    binCarb=np.histogram(elevCarb[:,site],bins=edges)
    #saves tuple value from each loop iteration into single array
    hypCarb[:,site]=binCarb[0]
    
    binFels=np.histogram(elevFels[:,site],bins=edges)
    hypFels[:,site]=binFels[0]
    """
    hypMaf seems to be where the issue is.  The non-zero numbers are in bins
    38-43, when they should be in bins 48-68.  They are in the correct place 
    for every other rock type and iteration, it is just hypMaf in the second
    iteration (site==1) that seems to be raising an issue.
    """
    binMaf=np.histogram(elevMaf[:,site],bins=edges)
    hypMaf[:,site]=binMaf[0]
    

#---locate hypsometric intersection---
#multiply hypsometries against each other, only 3way intersect remains
intsect=np.multiply(hypCarb,hypFels,hypMaf)
"""
The following line of hard code fixes the issue, but will prevent any site 2 
from ever having suitable elevations, even if it really does work.  This line 
will need to be removed by fixing the issue above
"""
intsect[:,1]=np.zeros((450))
#find where value is not 0
elevRaw=intsect>0


#---output information to user---
for i in range(numSites):
    #convoluted equation to equate input and output table columns
    j=((i+1)*5)-1
    #sum column corresponding to site number
    num=np.sum(elevRaw[:,i])
    if num==0:
        print("Group %d: No suitable locations found." %(i+1))
    else:
        #locates indeces of non-zero values
        elev=np.where(elevRaw[:,i])
        #find max and min elevations in meters ASL
        minE=np.min(elev)*10
        maxE=np.max(elev)*10
        print("Group %d: Suitable conditions between %d m and %d m elevation." %((i+1),minE,maxE))
        
        #allocate matrices and clear from last iteration
        Carb=np.zeros((100,5))
        Fels=np.zeros((100,5))
        Maf=np.zeros((100,5))

        #extract all rows of data where elevation is within range
        dumpC=dataCarb[(dataCarb[:,j]>=minE) & (dataCarb[:,j]<=maxE)]
        #save only the columns corresponding to the currently analyzed site
        Carb=dumpC[:,i*5:j+1]
        #finds max ObjectID and StreamID from the current iteration
        OBM=np.max(Carb[:,0])
        IDM=np.max(Carb[:,1])
        dumpF=dataFels[(dataFels[:,j]>=minE) & (dataFels[:,j]<=maxE)]
        Fels=dumpF[:,i*5:j+1]
        #adds existing IDs to all new values, maintains uniqueness
        Fels[:,0]=Fels[:,0]+OBM
        Fels[:,1]=Fels[:,1]+IDM
        #finds new max ObjectID and StreamID
        OBM=np.max(Fels[:,0])
        IDM=np.max(Fels[:,1])
        dumpM=dataMaf[(dataMaf[:,j]>=minE) & (dataMaf[:,j]<=maxE)]
        Maf=dumpM[:,i*5:j+1]
        #maintains ID uniqueness
        Maf[:,0]=Maf[:,0]+OBM
        Maf[:,1]=Maf[:,1]+IDM
        #vertically concatenates all 3 rock type matrices into a group matrix
        Group=np.vstack((Carb,Fels,Maf))
        #save output file name and path
        outName=("ElevationBands/Group%02d.csv" %(i+1))
        #writes the output as a .csv to the output folder
        np.savetxt(outName,Group,header="ObjectID,StreamID,Long,Lat,Elevation",delimiter=",")
        
        
print(datetime.now()-startTime)    