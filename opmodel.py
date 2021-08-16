import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from scipy.interpolate import griddata
import os


def modelPredict(time_input, mdl_type,df_model,full_extent,predictors,Mdl,shape_feature):
    df_model["uv10"]= np.sqrt((df_model["u10"]*df_model["u10"]+ df_model["v10"]*df_model["v10"]).tolist())
    df_model["Month"] = 1



    predict_df= df_model.loc[:,predictors]
    predict_df["predictions"]= Mdl.predict(predict_df)
    # predict_in_out = pd.concat([predict_in, predict_out],axis=1)

    predict_out = predict_df["predictions"]


    ### Prediection result visualization

    ## mager the predicted table to the full extend for plotting purpose
    merged = pd.merge(full_extent,predict_out, left_index=True, right_index=True,how="left")

    # plot a table with coordinates columns
    x_flat = merged["Longitude"]
    y_flat = merged["Latitude"]
    arr_flat = merged["predictions"]


    xi = np.linspace(-125,-65,480)
    yi = np.linspace(25,50,330)
    xi,yi = np.meshgrid(xi,yi)
    zi = griddata((x_flat, y_flat),arr_flat, (xi,yi), method='nearest')

    
    
    if not os.path.exists(mdl_type + "EstimatedPM25"):
        os.makedirs(mdl_type + "EstimatedPM25")
    
    fig=plt.figure(figsize=[20,13])
    ax = plt.subplot(projection=ccrs.PlateCarree())
    ax.add_feature(shape_feature,edgecolor='blue')
    ax.gridlines(draw_labels=True)
    ax.coastlines()
    c = ax.pcolor(xi,yi,zi,cmap='coolwarm', vmin=0,vmax=20)
    cax = plt.axes([0.95, 0.25, 0.04,0.5 ])
    fig.colorbar(c, cax=cax)
    plt.savefig(os.path.join(mdl_type + "EstimatedPM25","PredictedAOD_"+time_input +".png"))
    

#     # Convert ndarray data with regular coords to xarray objects
#     ds_NEXREG = xr.DataArray(zi, coords=[yi[:,1], xi[0]], dims=["lat", "lon"])

#     fig = plt.figure(figsize=[20,13])
#     ax = plt.subplot(projection=ccrs.PlateCarree())
#     ax.add_feature(shape_feature,edgecolor='blue')
#     ax.gridlines(draw_labels=True)
#     ax.coastlines()
#     ds_NEXREG.plot(cmap=plt.cm.coolwarm, x='lon', y='lat')
#     print ("Boundry: %f,%f,%f,%f" %(x_min, x_max, y_min, y_max))
#     plt.savefig("AOD_trim_grid.png")

    merged.to_csv(os.path.join(mdl_type+ "EstimatedPM25","EstimatedPM25"+time_input +".csv"))