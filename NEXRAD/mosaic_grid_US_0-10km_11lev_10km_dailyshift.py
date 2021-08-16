import numpy as np
import datetime
import pyart
import boto
import os
import tempfile
import matplotlib as mpl
import matplotlib.pyplot as plt
# import Basemap
# from mpl_toolkits.basemap import Basemap
import time
#suppress deprecation warnings
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)
import moviepy.editor as mpy
#import dill
import pickle
from pathlib import Path
import glob
import gc
import sys

###############################################################################################################################

def plot_grid(grid,plotVariable = 'reflectivity',level = 13):
               
    fig = plt.figure(figsize=[15, 8])
    ax = fig.add_subplot(111)
    displaygrid = pyart.graph.GridMapDisplayBasemap(grid)
    displaygrid.plot_basemap(lat_lines=(25,30,35,40,45,50), lon_lines=(-120,-110,-100,-90,-80,-70))
    displaygrid.plot_grid(plotVariable, level, vmin=-20, vmax=40,
                 cmap = pyart.graph.cm.NWSRef)
    fig.savefig(os.path.join("./plot/", grid.time["units"] +str(level) + ".png"), format='png', dpi=200)
    print("Map saved")
    
#     grid.write('Mosaic_grid05_US', format='NETCDF4', arm_time_variables=False, arm_alt_lat_lon_variables=False)
#     print("Grid saved")
    
#     pyart.io.write_grid_geotiff(grid, "Mosaic_grid_US", 'reflectivity', rgb=False, level=None, cmap='viridis', vmin=0, vmax=75, color_levels=None, warp=False, sld=False, use_doublequotes=False)
#     print("Geotiff saved")
###############################################################################################################################
def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1]
    return li_dif

#get all sites' name
def get_allsites():
    all_sites = []
    locs = pyart.io.nexrad_common.NEXRAD_LOCATIONS
    for key in locs:
        all_sites.append(key)
    return all_sites
###############################################################################################################################

def customized_download(date='2020/05/16',time=190000,all_sites=['KFWS','KDYX'],download = "NO"):

    #create a datetime object for the current time in UTC and use the
    # year, month, and day to drill down into the NEXRAD directory structure.
    #now = datetime.datetime.utcnow()
    #pirnt(now)
    #date = ("{:4d}".format(now.year) + '/' + "{:02d}".format(now.month) + '/' +
    #        "{:2d}".format(now.day) + '/')

    #----------------------------------------------------------
#     date = '2020/01/28/'
#     time = 220000
#     #all_sites = get_allsites()

#     # assign a target site for testing purpose
#     all_sites = ['KFWS']
    #---------------------------------------------------------

    print("Search Time %s %s" %(date, time))
    print(all_sites)

    radars = []
    i = 0
    count = 1
    awscount = 0
    Fail_lst =[]
    awslst = []
    #get the bucket list for the selected date

    #use boto to connect to the AWS nexrad holdings directory
    s3conn = boto.connect_s3()
    bucket = s3conn.get_bucket('noaa-nexrad-level2')

    #Note: this returns a list of all of the radar sites with data for
    # the selected date
    ls = bucket.list(prefix=date + '/',delimiter='/')
    for item in ls:
        awslst.append(item.name.split('/')[-2])

    #Find the Missing sites from AWS lst
    li3 = Diff(awslst, all_sites)
    print("Missing sites : %s " %(li3))

    for key in ls:
        #print(key.name)
        awscount+=1
    print("%d sites are selected, total %d sites returned from AWS at %s %s" %(len(all_sites)-len(li3),awscount-1,date,time))
    print("===================================================================================")
    print('\n')

    for site in all_sites:
        for key in ls:
            #only pull the data and save the arrays for the site we want
            if site in key.name.split('/')[-2]:
                print("%s has been found in AWS return list (%d/%d)" %(site,count,awscount-1))
                #set up the path to the NEXRAD files
                path = date +'/' + site + '/' + site
                #grab the last file in the file list
                keys = bucket.get_all_keys(prefix=path)

                #find the file closest to myTime
                temp = 0
                minimum = 20000
                for key in keys:
                    radarTime = int(key.name.split('/')[-1].split('_')[1])
                    temp = abs(int(time) - radarTime)
                    #print(temp)
                    if temp < minimum:
                        minimum = temp
                        fname = key
                try:
                    print(fname)

                    #get the file
                    s3key = bucket.get_key(fname)
                    #save a temporary file to the local host
                    localfile = tempfile.NamedTemporaryFile()
                    #write the contents of the NEXRAD file to the temporary file
                    s3key.get_contents_to_filename(localfile.name)
                    print(localfile.name)
                    #use the read_nexrad_archive function from PyART to read in NEXRAD file

                    radars.append(pyart.io.read_nexrad_archive(localfile.name))
                    #get the date and time from the radar file for plot enhancement
                    fileTime = radars[i].time['units'].split(' ')[-1].split('T')
                    print(site + ' ' + 'has been read and added to radars list' + ': ' + fileTime[0] + ' at ' + fileTime[1] )
                    i+=1
                    count+=1
                    print('\n')
                except:
                    print("%s not read sucsseful <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" %(site))
                    Fail_lst.append(site)
                    print('\n')
    print("Failed reading sites %s" %(Fail_lst))
    
     # check all radar objects are valid
    print("%d radars objects are saved in radar list " %len(radars))
    field_names = ['reflectivity','velocity','spectrum_width',
            'differential_phase','differential_reflectivity','cross_correlation_ratio']
    remove_list = []
    
    for i in range(len(radars)):
        try:
            for field_name in field_names:
                radars[i].check_field_exists(field_name)
        except:
            remove_list.append(i)
            

    for index in sorted(remove_list, reverse=True):
        del radars[index]
        
    print("%d radar obejcts are valid with all six variables " % len(radars))
    
    
    Path(os.path.join(date.replace("/","-")[:7],date.replace("/","-"),time)).mkdir(parents = True, exist_ok=True)
    if download == "YES":
        print("Saving radars object ......")
        
        pickle.dump(radars, open(os.path.join(date.replace("/","-"),time,date.replace("/","-") + "_" + time +"_" + 'radars.pickle'), 'wb'))
    return radars
    
    
###############################################################################################################################
    
    
def mosaic_radar(radars,
               grid_shape =(11, 330, 480),
               grid_limits=((0, 10001), (-1100000, 2200000), (-2400000, 2400000)),
               grid_origin = (32.57861, -97.303611),
               date= 0,
               time = 0):
    
    print("Converting radar to grid......")
    grid = pyart.map.grid_from_radars(
    radars,
    grid_shape=grid_shape,
    grid_limits=grid_limits,
    grid_origin = grid_origin,
    gridding_algo='map_gates_to_grid',
    fields=['reflectivity','velocity','spectrum_width',
            'differential_phase','differential_reflectivity','cross_correlation_ratio'])
    
    print("Mosaic grid created")
    
#     print("Plottting radar map......")
#     fig = plt.figure(figsize=[15, 8])
#     ax = fig.add_subplot(111)
    
#     displaygrid = pyart.graph.GridMapDisplayBasemap(grid)
#     displaygrid.plot_basemap(lat_lines=(25,30,35,40,45,50), lon_lines=(-120,-110,-100,-90,-80,-70))
#     displaygrid.plot_grid(plotVariable, level=0, vmin=-20, vmax=40,
#                  cmap = pyart.graph.cm.NWSRef)
    
    
    
    
    
#     fig.savefig(os.path.join("./plot/"+str(date), grid.time["units"] + ".png"), format='png', dpi=200)
#     print("Map saved")
    grid.write(os.path.join("NEXRAD",date.replace("/","-")[:7],date.replace("/","-"), time,date.replace("/","-") + "_" + time + ".nc"), format='NETCDF4', arm_time_variables=False, arm_alt_lat_lon_variables=False)
    print("Grid saved")
    
#     pyart.io.write_grid_geotiff(grid, os.path.join(date.replace("/","-")[:7],date.replace("/","-"), time, date.replace("/","-") +"_" + time), 'reflectivity', rgb=False, level=None, cmap='viridis', vmin=0, vmax=75, color_levels=None, warp=False, sld=False, use_doublequotes=False)
#     print("Geotiff saved")
    
    return grid
    
    
    
###############################################################################################################################
    
def plot_grid_elevation(grid,date,time,plotVariable = 'reflectivity'):
        # Plot radars at each elevation and create the gif movie

    #images = []
    for i in range(11):
        fig = plt.figure(figsize=[15, 8])
        #ax = fig.add_subplot(111)

        displaygrid = pyart.graph.GridMapDisplayBasemap(grid)
        displaygrid.plot_basemap(lat_lines=(25,30,35,40,45,50), lon_lines=(-120,-110,-100,-90,-80,-70), auto_range=True, min_lon=-120, max_lon=-70, min_lat=25, max_lat=50) # extent for US
        
            
        displaygrid.plot_grid(plotVariable, level=i, vmin=-20, vmax=40,
                         cmap = pyart.graph.cm.NWSRef
        ,title = "USA Mosaic at %2.1f km %s %s %s"%(i, date, time, plotVariable))
        
        plt.savefig(os.path.join(date.replace("/","-")[:7],date.replace("/","-"),time, date.replace("/","-")+ "_" + time +  "_" + "level" + "_" + str(f"{i:02d}")+ ".png") )
        #images.append(plt)
        print("level %d image saved" %(i))
        plt.close()
        
        
#     for i in range(20,101,10):
#         fig = plt.figure(figsize=[15, 8])
#         #ax = fig.add_subplot(111)

#         displaygrid = pyart.graph.GridMapDisplayBasemap(grid)
#         displaygrid.plot_basemap(lat_lines=(25,30,35,40,45,50), lon_lines=(-120,-110,-100,-90,-80,-70), auto_range=True, min_lon=-92, max_lon=-86, min_lat=25, max_lat=44) # extent for dallas
        
# #         displaygrid.plot_basemap(lat_lines=(25,30,35,40,45,50), lon_lines=(-120,-110,-100,-90,-80,-70), auto_range=True, min_lon=-92, max_lon=-86, min_lat=25, max_lat=44) # extent for US
            
#         displaygrid.plot_grid(plotVariable, level=i, vmin=-20, vmax=40,
#                          cmap = pyart.graph.cm.NWSRef)
#         #,title = "U.S Mosaic at %2.1f km %s %s %s"%(i*0.1, date, time, plotVariable) 
        
#         plt.savefig(os.path.join(date.replace("/","-"),time, date.replace("/","-")+ "_" + time +  "_" + "level" + "_" + str(f"{i:02d}")+ ".png") )
#         #images.append(plt)
#         print("level %d image saved" %(i))


###############################################################################################################################

def make_gif(date,time,fps=5, gif_name = 'KFWS_matchPlot'):
    folder=os.path.join(date.replace("/","-")[:7],date.replace("/","-"),time)
    file_list = glob.glob(folder+'/*.png')
    print(file_list)
    list.sort(file_list, key=lambda x: int(x.split('_')[3].split('.png')[0])) # Sort the images by #, this may need to be tweaked for your use case
    clip = mpy.ImageSequenceClip(file_list, fps=fps)
    clip.write_gif(os.path.join(date.replace("/","-")[:7],date.replace("/","-"),time,'{}.gif'.format(gif_name)), fps=fps)

   

########################################################################################################
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)
        
########################################################################################################
def implement_mosaic(yr,mon,day):

    start_dt = datetime.date(yr,mon,day)  
    end_dt = datetime.date(yr,mon,day)
#     TimeRange = ['000000','010000','020000','030000','040000','050000','060000','070000','080000','090000','100000','110000','120000','130000','140000','150000','160000','170000','180000','190000','200000','210000','220000','230000']


#     TimeRange = ['003000','013000','023000','033000','043000','053000','063000','073000','083000','093000','103000','113000','123000','133000','143000','153000','163000','173000','183000','193000','203000','213000','223000','233000']
    TimeRange = ['173000']
    
    for dt in daterange(start_dt, end_dt):
        for myTime in TimeRange:
            start_time = time.time()
            #check if target mosaic exists, if yes then plot directly
                
            if Path(os.path.join("NEXRAD",dt.strftime("%Y-%m"),dt.strftime("%Y-%m-%d"), myTime,dt.strftime("%Y-%m-%d") + "_" + myTime + ".nc")).exists():
                
                print("%s exists, search the next time stamp......" %(os.path.join("NEXRAD",dt.strftime("%Y-%m"),dt.strftime("%Y-%m-%d"), myTime,dt.strftime("%Y-%m-%d") + "_" + myTime + ".nc")))

                             
                
            else:
                radars =customized_download(date=dt.strftime("%Y/%m/%d"),time=myTime,all_sites=all_sites,download = 'NO')

                    
                try:
                    grid = mosaic_radar(radars,date=dt.strftime("%Y/%m/%d"),time = myTime)
#                     plot_grid_elevation(grid,dt.strftime("%Y/%m/%d"),myTime)

#                     make_gif(dt.strftime("%Y/%m/%d"), myTime, gif_name = dt.strftime("%Y-%m-%d") +"_"+ myTime)
                    print("--- %s seconds ---" % (time.time() - start_time))
                    del grid,radars
                    gc.collect()
                except:
                    print("convert failed")
                    del radars
                    gc.collect()

#####################################################################################################
if __name__ == "__main__":
    
#     now = datetime.datetime.utcnow()
#     myDate = ("{:4d}".format(now.year) + '/' + "{:02d}".format(now.month) + '/' +"{:02d}".format(now.day))
#     myTime = ("{:02d}".format(now.hour)  + "{:02d}".format(now.minute)  +"{:02d}".format(now.second) )
#     outPut_file = os.path.join(myDate,myTime,"nohup.txt")


    #grid = pyart.io.read_grid(path)
    
## Run the code with start date and end date: example  2019 12 29 2019 12 30   
## Start date and end date could be set to the same day.
    all_sites=get_allsites()
    
    yr = int(sys.argv[1])
    mon = int(sys.argv[2])
    day = int(sys.argv[3])

    implement_mosaic(yr,mon,day)
    
    
    