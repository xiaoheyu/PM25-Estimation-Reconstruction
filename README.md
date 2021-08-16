# PM25-Estimation-Reconstruction

The folder includes codes that accpet pretrained model as input parameters to make hourly pm2.5 estiamtions at 10km spatial resolution covering the US. 
The output includes a PM2.5 estiamtion plot and a dataframe for each time stamp.

Input predictor variables includes meterological parameters form ECMWF, Next Generation Weather Radar, GOES16 AOD, soil type, population density, elevation, 
landcover, and Global lithology. Among these variables, ECMWF and GOES16 AOD will be automatically downloaded with the code, the rest static variables will be stored in a seprated cloud stoagre due to the large size.

To run the code, put the downloaded static variable directly under the folder PM25-Estimation-Reconstruction.

Code sample:
opMain.py 2020 01 06 2020 01 06   # Make hourly average pm2.5 estimation on 2020/01/06 
opMain.py 2020 01 06 2020 01 08   # Make hourly average pm2.5 estimation through  2020/01 06 to 2020/01/08 


####################################################################################################################################################################




