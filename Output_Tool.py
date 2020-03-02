"""
Functions designed to be used as UDF in Excel.  The functions are dependent on
arguments coming from Visual Basic inside Excel

All functions are designed to run through a User Defined Function "Grey Button"
within the Output_Tool.xlsm file 

@author: Derek Holsapple
"""
import pandas as pd  
import numpy as np
import os            
import xlwings as xw 
import shutil        
import zipfile      
from Processing.rawDataImport import rawDataImport
from Processing.finalOutputFrame import finalOutputFrame
from Processing.cleanRawOutput import cleanRawOutput
from Processing.closestLatLon import closestLatLon
from Processing.utility import utility
from Processing.customCalculations import customCalculations
from Map.mapTemp import mapTemp
from Map.plotSite import plotSite
from Map.mapGenerator import mapGenerator


def extractAllZip_Files( path ):
    '''
    XL Wings FUNCTION
    
    extractAllZip_Files()
    
    Given a root directory the method will extract all files in sub-directories
    and place them in a destination directory.  CUrrently can process zipped,
    ipw and csv files and place into one single directory
    
    @param path        - String, the path of where you want the program to start 
                                    unzipping files
                            i.e. the program will extract every sub directory 
                                    beyond this path
    @return void       - Program will store extracted files into the 
                                    Python_RawData_Combined directory
    '''
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############
    myWorkBook.sheets[mySheet].range(32,4).value = "Unzipping Files"
    #Delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(path + '\\Python_RawData_Combined'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    #########
    #Search for zipped csv files
    #########
    zippedFiles = []
    # Use os walk to cycle through all directories and pull out .zip files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".zip"):
                zippedFiles.append(os.path.join(dirpath, x))
            elif x.endswith(".ZIP"):
                zippedFiles.append(os.path.join(dirpath, x))            
    #ReferenceXL wings to give user feedback
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( zippedFiles )
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    
    # Unzip all the files and put them into the directory
    for i in range(0 , len( zippedFiles ) ):
        with zipfile.ZipFile( zippedFiles[i] ,"r") as zip_ref:
            # Directory to put files into
            zip_ref.extractall(path + '\Python_RawData_Combined')
        myWorkBook.sheets[mySheet].range(35,4).value = i + 1
    #########
    #Search for csv files through the directories
    #########
    myWorkBook.sheets[mySheet].range(32,4).value = \
                                        "Searching and Relocating CSV Files"
    cSV_Files = []
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".csv"):
                cSV_Files.append(os.path.join(dirpath, x))
            elif x.endswith(".CSV"):
                cSV_Files.append(os.path.join(dirpath, x))             
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( cSV_Files )
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    # Move all CSV files and put them into the directory  
    for i in range(0 , len( cSV_Files ) ):   
        shutil.copy(cSV_Files[i], path + '\Python_RawData_Combined')
        myWorkBook.sheets[mySheet].range(35,4).value = i + 1   
    #########
    #Search for epw files through the directories
    #########            
    myWorkBook.sheets[mySheet].range(32,4).value = \
                                        "Searching and Relocating .epw Files"    
    ePW_Files = []     
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".epw"):
                ePW_Files.append(os.path.join(dirpath, x))
            elif x.endswith(".EPW"):
                ePW_Files.append(os.path.join(dirpath, x))               
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( ePW_Files )
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    myWorkBook.sheets[mySheet].range(35,4).value =  len( ePW_Files )        
    # Move all .epw files and put them into the directory  
    for i in range(0 , len( ePW_Files ) ):
        shutil.copy(ePW_Files[i], path + '\Python_RawData_Combined')
        myWorkBook.sheets[mySheet].range(35,4).value = i + 1        
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( ePW_Files )
    myWorkBook.sheets[mySheet].range(32,4).value = "Restructuring data"
    dir_name = path + '\Python_RawData_Combined'
    allFiles = os.listdir(dir_name)
    for item in allFiles:
        if item.endswith(".WY3"):
            os.remove(os.path.join(dir_name, item))    
    myWorkBook.sheets[mySheet].range(32,4).value =  "File Organization Complete"
    myWorkBook.sheets[mySheet].range(34,6).value =  ''
    myWorkBook.sheets[mySheet].range(35,6).value =  ''
    myWorkBook.sheets[mySheet].range(34,4).value =  ''
    myWorkBook.sheets[mySheet].range(35,4).value =  ''  



def createPickleFiles( currentDirectory ):
    '''
    XL Wings FUNCTION
    
    createPickleFiles()
    
    Aggregate raw data (TMY3, CWEC, IWEC, Satellite Data) into individual pickle files
    
    @param currentDirectory  - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @return void             - pickle containig tuples of (series:location data, dataframe:metadata)               
    '''
    #XL Wings
    ##############
    # Use the xlwings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############  
    path = currentDirectory
    
    myWorkBook.sheets[mySheet].range(48,4).value = \
                            "Delete all content from previous processing"                        
    #Delete the content of the folder.
    utility.deleteAllFiles( path + \
                              '\\Pandas_Pickle_DataFrames\\Pickle_RawData')
    utility.deleteAllFiles(  path + \
                              '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows')

    myWorkBook.sheets[mySheet].range(48,4).value = \
                                "Merging IWEC, CWEC, TMY3 and Satellite data together"
    myWorkBook.sheets[mySheet].range(50,6).value = "Total Files"
    # Get a list of all the raw files
    numFiles = len( rawDataImport.rawFilesNamesList( path ) )
    myWorkBook.sheets[mySheet].range(51,6).value = numFiles

    rawDataImport.rawDataToTuple( path ) 

    myWorkBook.sheets[mySheet].range(48,4).value = "Pickles Sucessfully Saved"
    
    

def createLevel_1_Pickles( currentDirectory , selector, max_angle, gcr): 
    '''
    XL Wings FUNCTION
    
    createPickleFiles()
    
    Import the raw pickle files.  Process the raw pickle files and return solar 
    position and irradiance.  Store the processed data as pickles in the following 
    directory
    \Pandas_Pickle_DataFrames\Pickle_Level1
    
    @param currentDirectory     - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @ param selector             - String, "fixedTilt" : solar module at fixed tile (latitude tilt)
                                           "singleAxisTracker": solar module with single axis tracker 
                                                (modules will be facing east/west with axis bar facing north/south)
    @param max_angle              -int, angle of rotation capability of single axis module
                                            *90 is standard, 180 will allow full rotation, i.e the panel can filp upside down
    @param gcr                   -float, Ground Cover Ratio of a single axis-system
                                         A tracker system with modules 2 meters wide,
                                         centered on the tracking axis, with 6 meters 
                                         between the tracking axes has a gcr of 2/6=0.333[3].                                        
    
     @return void               - Will convert dataframes into pickle datafiles  
                    *Note: each location will be saved as its own .pickle file                 
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############

    #First delete the content of the folder you will be sending the files to.
    
    
    
    if selector == 'fixedTilt':
        
        myWorkBook.sheets[mySheet].range(64,4).value = "Processing Files"
        myWorkBook.sheets[mySheet].range(66,4).value = "Files Processed"
        myWorkBook.sheets[mySheet].range(66,6).value = "Total Files"
              
        utility.deleteAllFiles( currentDirectory + \
                                  '\\Pandas_Pickle_DataFrames\\Pickle_Level1' )
        utility.deleteAllFiles( currentDirectory + \
                            '\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary')
        
        
    elif selector == 'singleAxisTracker':
        
        myWorkBook.sheets[mySheet].range(64,13).value = "Processing Files"
        myWorkBook.sheets[mySheet].range(66,13).value = "Files Processed"
        myWorkBook.sheets[mySheet].range(66,15).value = "Total Files"        
        
        utility.deleteAllFiles( currentDirectory + \
                        '\\Pandas_Pickle_DataFrames\\Pickle_Level1_SingleAxisTracker' )
        utility.deleteAllFiles( currentDirectory + \
                        '\\Pandas_Pickle_DataFrames\\Pickle_Level1_SingleAxisTracker_Summary')

    
    finalOutputFrame.moduleProcessing_toPickle( currentDirectory , selector , max_angle, gcr)
    # User feedback
    myWorkBook.sheets[mySheet].range(64,4).value = "All Files Sucessfully Saved"


def outputFileSummaryPostProcess( currentDirectory , selector ):
    '''
    XL Wings FUNCTION
    
    Take a summary dataframe from the helper method and output a report to a 
    generated excel sheet
    
    @param currentDirectory      - String, where the excel file is located 
                                    (passed as an argument from EXCEL if using UDF) 
    @ param selector             - String, "fixedTilt" : solar module at fixed tile (latitude tilt)
                                           "singleAxisTracker": solar module with single axis tracker 
                                                (modules will be facing east/west with axis bar facing north/south)                               
    @return void                 - Creates a summary csv of all data
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    path = currentDirectory
    # create a summary data frame
    
    if selector == 'fixedTilt':
        summary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\' + \
                            'Pickle_Level1_Summary\\Pickle_Level1_Summary.pickle')
    elif selector == 'singleAxisTracker':
        summary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\' + \
                    'Pickle_Level1_SingleAxisTracker_Summary\\Pickle_Level1_SingleAxisTracker_Summary.pickle')
    columnHeaders_list = list(summary_df)  
    myWorkBook.sheets[mySheet].range(10,1).value = columnHeaders_list
    myWorkBook.sheets[mySheet].range(11,1).value = summary_df.values.tolist()
 
    

def search_Level1_Pickle_Output( currentDirectory , userInput):    
    '''
    XL Wings METHOD
    
    search_Level1_Pickle_Output()
    
    1) Take user input "unique Identifier" 
    2) Search the pickle files for a match
    3) Output the raw pickle data to the excel sheet
    
    @param path      -String, path to the folder where this .py file is located
    @param userInput -String, unique Identifier of a location found on sheet one 
    
    @return void    - Output of raw data to excel sheet two
    '''
    #XL Wings
    #############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller()
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[2]
    #############
    path = currentDirectory
    rawfileNames = cleanRawOutput.filesNameList( path )
    uniqueID_List = cleanRawOutput.stringList_UniqueID_List(rawfileNames)

    for i in range(0 , len( rawfileNames ) ):
        #If the user input is a match with a raw data file
        if userInput == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            data_tuple = pd.read_pickle( path + \
                '/Pandas_Pickle_DataFrames/Pickle_Level1/' + rawfileNames[i] )
            #Unpack the tuple
            location_series , raw_df = data_tuple
            rawcolumnHeaders_list = list(raw_df)
            myWorkBook.sheets[mySheet].range(9,1).value = rawcolumnHeaders_list
            myWorkBook.sheets[mySheet].range(10,1).value = raw_df.values.tolist()
            myWorkBook.sheets[mySheet].range(6,1).value = location_series.index.tolist()
            #nan value do not transfer to excel
            location_series = location_series.replace(np.nan, 'NONE', regex=True)
            location_series = location_series.replace('', 'NONE', regex=True)
            location_series = location_series.replace('unknown', 'NONE', regex=True)
            
            myWorkBook.sheets[mySheet].range(7,1).value =  location_series.tolist()
            #Stop the search for loop once the file is located
            break



def closest_Cities( currentDirectory ,  lat1 , lon1 ):
    '''
    XL Wings FUNCTION
    
    createPickleFiles()
    
    Ask the user to enter a point of interest in Latitude and Longitude in Decimal 
    Degrees.  Return a summary of distances closest to the point of interest. 
    The summary will be sorted from smallest distance to greatest distance.
    
    param@ currentDirectory   - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
     @param lat1              - Float , Decimal Degrees of the latitude 
                                       (passed as an argument from EXCEL using UDF)
     @param lon1              - Float , Decimal Degrees of the longitude 
                                       (passed as an argument from EXCEL using UDF)
     @return void               - return a summary to excel with locations sorted 
                                     from shortest distance to greatest distance                 
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    myWorkBook.sheets[mySheet].range(6,1).value = "Distance From (km)"
    myWorkBook.sheets[mySheet].range(7,1).value = "Latitude"
    myWorkBook.sheets[mySheet].range(8,1).value = lat1
    myWorkBook.sheets[mySheet].range(7,2).value = "Longitude"
    myWorkBook.sheets[mySheet].range(8,2).value = lon1
    closestLocation_df , columnNames_list = \
        closestLatLon.closestLocationFrame( currentDirectory ,  lat1 , lon1 )
    myWorkBook.sheets[mySheet].range(11,1).value = \
        closestLocation_df.values.tolist()
    myWorkBook.sheets[mySheet].range(10,1).value = columnNames_list



def createTempMap(path , mapSelect ):
    '''
    XL Wings FUNCTION
    
    createTempMap()
    
    Import the processed map pickle and create a map using the Bokeh package.
    Bokeh will render a html file containing the map. 
    
    @param path       - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param mapSelect  - String, used to select what type of map to render
                                - See "MapDewYield.py" for exact string to pass                                  
    
    @return void      - Will render a map          
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    xw.Book.caller() 
    #Reference sheet 0    
    ##############
    mapTemp.outputMapTemp(path , mapSelect )



def outputMapDriver( currentDirectory , mapType ):
    '''
    XL Wings FUNCTIONS
    
    outputMapDriver()
    
    Driver to render a map. 
    
    @param currentDirectory    - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param mapType              - String,  select what map to generate

        Annual GHI
        Annual DNI
        Annual DHI
        Annual POA Global Irradiance
        Annual POA Direct Irradiance
        Annual POA Diffuse Irradiance
        Annual POA Sky Diffuse Irradiance
        Annual POA Ground Diffuse Irradiance
        Annual Global UV Dose
        Annual UV Dose at Latitude Tilt
        
        Annual Minimum Ambient Temperature
        Annual Average Ambient Temperature
        Annual Maximum Ambient Temperature
        Annual Range Ambient Temperature
        Average of Yearly Water Vapor Pressure
        Sum of Yearly Water Vapor Pressure
        Annual Hours Relative Humidity > 85%
        Sum of Yearly Dew
        
      **CUSTOM MAPS**
       Acceleration Factor
       Sum Rate of Degradation Environmnet
       Avg Rate of Degradation Environmnet
                           
    @return void               - Void, Renders a world map          
    '''    
    mapGenerator.mapGeneratorDriver(currentDirectory , mapType)



def outputPlotDriver( currentDirectory , fileID , selector ):
    '''
    XL Wings FUNCTIONS
    
    outputPlotDriver()
    
    Driver to render a plot of individual site data. 
    
    @param currentDirectory    - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param fileID              - String, unique ID of site specific location
                                                                 
    @param selector            - String, select what type data to plot
                                
    @return void               - Void, Renders a data plot of a individual site          
    '''    
    plotSite.xLWingsInterfacePlot( currentDirectory , fileID , selector )
    
    
def outputVantHoffCalc( currentDirectory , configType , refTemp , Tf , x , Ichamber ):
    '''
    XL Wings FUNCTIONS
    
    outputVantHoffCalc()
    
    Driver to calculate Van Hoff Calculation from custom user input parameter 
    passed from XLWings
    
    @param currentDirectory    - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param configType            -string, name of the dataframe column containing temperature
                                      'Cell Temperature(open_rack_cell_glassback)(C)'
                                      'Cell Temperature(roof_mount_cell_glassback)(C)'
                                      'Cell Temperature(open_rack_cell_polymerback)(C)'
                                      'Cell Temperature(insulated_back_polymerback)(C)'                                        
                                      'Cell Temperature(open_rack_polymer_thinfilm_steel)(C)' 
                                      'Cell Temperature(22x_concentrator_tracker)(C)'
    @param refTemp               -float, reference temperature (C) "Chamber Temperature"  
    @param Tf                    -float, multiplier for the increase in degradation
                                      for every 10(C) temperature increase                                          
    @param x                     -float, fit parameter
    @param Ichamber              -float, Irradiance of Controlled Condition W/m^2                                                                 
                                
    @return void                 - Void, Renders a map of custom Van Hoff Calculation          
    '''    
    
    vantHoff_df = customCalculations.generateVantHoffSummarySheet(configType,
                                                                  refTemp ,
                                                                  Tf , 
                                                                  x , 
                                                                  Ichamber , 
                                                                  currentDirectory )    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
#    myWorkBook = xw.Book( currentDirectory + r'\Output_Tool.xlsm' )
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[4]
    ##############

    vantHoff_df  = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\' + \
                        'Pickle_CustomCals\\vantHoffSummary.pickle')
    
    inputDataColumns = ['Module Type at Latitude Tilt', 'Tchamber', 'Tf', 'x', 'Ichamber']
    inputData_List = [configType[17:-4], refTemp , Tf , x , Ichamber]
    myWorkBook.sheets[mySheet].range(17,1).value = inputDataColumns    
    myWorkBook.sheets[mySheet].range(18,1).value = inputData_List    
    
    columnHeaders_list = list(vantHoff_df)  
    myWorkBook.sheets[mySheet].range(20,1).value = columnHeaders_list
    myWorkBook.sheets[mySheet].range(21,1).value = vantHoff_df.values.tolist()
    
   
    
  
    
#userInput = '711_30'
#currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'
#path = currentDirectory  
