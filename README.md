# Project Overview 
#### Please cite and refer to the paper for details.
#### There are 4 stages for the entire project.
#### Stage 1 (Code available in repo PM25-DataSource): Data download and visulization, including ECMWF, PBLH, GOES16-AOD, Landcover, Soil order, Population density, Elevation, and Lithology.
#### Stage 2 (Code available in repo PM25-DataMaching): Once data are downloaded, all variables will be macthed with PM2.5 groupd observation. A macthed data table is generated for machine learning model training.
#### Stage 3 (): Machine learning moldeing training
#### Stage 4 (Code available in repo PM25-Estimation-Reconstrcution or PM25-Estimation-Reconstrcution-Local ): Once model and data are ready, this code make pm25 estimations and generate visulization results.



# PM25-Estimation-Reconstruction


Please refer to the opMain.html for a jupyter lab demonstration of the PM2.5 estimation workflow. 


The folder includes codes that accpet pretrained model as input parameters to make hourly pm2.5 estiamtions at 10km spatial resolution covering the US. 
The output includes a PM2.5 estiamtion plot and a dataframe for each time stamp.


Input predictor variables includes meterological parameters form ECMWF, Next Generation Weather Radar, GOES16 AOD, soil type, population density, elevation, 
landcover, and Global lithology. Among these variables, ECMWF and GOES16 AOD will be automatically downloaded with the code, the rest static variables will be stored in a separate cloud drive due to the large size. NEXRAD is not a mandatoary input predictor for PM2.5 estimation. If needed, the NEXRAD mosaic for the US can be generated through the code in NEXRAD/mosaic_grid_US_0-10km_11lev_10km_dailyshift.py



To run the code, put the downloaded static variable directly under the folder PM25-Estimation-Reconstruction.
Code sample:
opMain.py 2020 01 06 2020 01 06   # Make hourly average pm2.5 estimation on 2020/01/06 
opMain.py 2020 01 06 2020 01 08   # Make hourly average pm2.5 estimation through  2020/01 06 to 2020/01/08 

(NEXRAD mosaic is only needed if model is set to NEXRAD mode )
mosaic_grid_US_0-10km_11lev_10km_dailyshift.py 2020 01 06 2020 01 06 # Generate mosaic in 2020/01/06 at hourly interval 
mosaic_grid_US_0-10km_11lev_10km_dailyshift.py 2020 01 06 2020 01 08 # Generate mosaic through 2020/01 06 to 2020/01/08 at hourly interval






