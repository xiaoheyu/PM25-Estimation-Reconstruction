# PM25-Estimation-Reconstruction

The folder includes codes that accpet pretrained model as input parameters to make hourly pm2.5 estiamtions at 10km spatial resolution covering the US. 
The output includes a PM2.5 estiamtion plot and a dataframe for each time stamp.

Input predictor variables includes meterological parameters form ECMWF, Next Generation Weather Radar, GOES16 AOD, soil type, population density, elevation, 
landcover, and Global lithology. Among these variables, ECMWF and GOES16 AOD will be automatically downloaded with the code, the rest static variables will be stored in a seprated cloud stoagre due to the large size.  NEXRAD is not an mandatoary input predictor for PM2.5 estimation. If needed, it can be download
through the code in NEXRAD/mosaic_grid_US_0-10km_11lev_10km_dailyshift.py



To run the code, put the downloaded static variable directly under the folder PM25-Estimation-Reconstruction.

Code sample:
opMain.py 2020 01 06 2020 01 06   # Make hourly average pm2.5 estimation on 2020/01/06 
opMain.py 2020 01 06 2020 01 08   # Make hourly average pm2.5 estimation through  2020/01 06 to 2020/01/08 

(NEXRAD mosaic is only needed if model is set to NEXRAD mode )
mosaic_grid_US_0-10km_11lev_10km_dailyshift.py 2020 01 06 2020 01 06 # Generate mosaic in 2020/01/06 at hourly interval 
mosaic_grid_US_0-10km_11lev_10km_dailyshift.py 2020 01 06 2020 01 08 # Generate mosaic through 2020/01 06 to 2020/01/08 at hourly interval


The opMain.html is and jupyter lab demonstration of the work estimation workflow. 





