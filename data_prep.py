import pandas as pd
import os
import numpy as np
import netCDF4 as nc
from sklearn.neighbors import KDTree
from scipy.interpolate import griddata
from datetime import datetime, timedelta
from pandarallel import pandarallel 

pandarallel.initialize(nb_workers=20, progress_bar=True)

GOES_DIR="/data/GOES/"
DATA_DIR="Data/"
OUT_DIR="/data/NASA2/"

suomi = pd.read_csv(DATA_DIR+"SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_7d.csv")
suomi = suomi[suomi['acq_date']=='2020-10-01']


GOES_FILES = []

for filename in os.listdir(GOES_DIR):
    if filename[-2:]=="nc":
        split = filename.split(".")[0].split("_")
        times = split[-3:]
        band_type = split[1]
        channel = band_type.split("-")[-1]
        metric_type = band_type[:-(len(channel)+1)]
        GOES_FILES.append((
            times[0][1:],
            times[1][1:],
            times[2][1:],
            metric_type,
            channel,
            os.path.join(GOES_DIR, filename)))
GOES_FILES = pd.DataFrame(GOES_FILES, columns=["start", "end", "creation", "metric", "channel", "path"])

goes_sorted = GOES_FILES.sort_values(['start', 'channel'])
goes_sorted = goes_sorted[goes_sorted['metric']=="ABI-L1b-RadC"]
goes_sorted = goes_sorted[goes_sorted['start'].str.startswith('2020275')].reset_index(drop=True)

goes_sorted['start'] = pd.to_datetime("20201001"+goes_sorted['start'].str[7:-1], format="%Y%m%d%H%M%S")
goes_sorted['end'] = pd.to_datetime("20201001"+goes_sorted['end'].str[7:-1], format="%Y%m%d%H%M%S")

suomi['timestamp'] = pd.to_datetime("20201001"+suomi['acq_time'].astype(str), format="%Y%m%d%H%M")

suomi['files'] = suomi['timestamp'].apply(lambda x: goes_sorted[(goes_sorted['end'] > x)]['path'].head(4).values)

def get_array(df):
    x = df['lon']
    y = df['lat']
    z = df['rad']
    xi = np.linspace(min(x),max(x), 100)
    yi = np.linspace(min(y),max(y), 100)

    X,Y = np.meshgrid(xi,yi)

    Z = griddata((x, y), z, (X, Y), method='cubic')
    return Z

def get_mat(latit, longi, data):
    data = nc.Dataset(data, "r")
    R = data.variables['Rad'][:].data
    proj_info = data.variables['goes_imager_projection']
    lon_origin = proj_info.longitude_of_projection_origin
    H = proj_info.perspective_point_height+proj_info.semi_major_axis
    r_eq = proj_info.semi_major_axis
    r_pol = proj_info.semi_minor_axis

    # Data info
    lat_rad_1d = data.variables['x'][:]
    lon_rad_1d = data.variables['y'][:]

    # close file when finished
    data.close()
    data = None

    # create meshgrid filled with radian angles
    lat_rad,lon_rad = np.meshgrid(lat_rad_1d,lon_rad_1d)

    # lat/lon calc routine from satellite radian angle vectors

    lambda_0 = (lon_origin*np.pi)/180.0

    a_var = np.power(np.sin(lat_rad),2.0) + (np.power(np.cos(lat_rad),2.0)*(np.power(np.cos(lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(lon_rad),2.0))))
    b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
    c_var = (H**2.0)-(r_eq**2.0)

    r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

    s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
    s_y = - r_s*np.sin(lat_rad)
    s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

    lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
    lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)
    data_df = pd.DataFrame({
            'lat':lat.data.flatten(),
            'lon':lon.data.flatten(),
            'rad':R.flatten(),
                    })

    bt = KDTree(data_df[['lat', 'lon']])
    data_df = data_df.loc[bt.query([latit, longi], 200)[1]]
    return get_array(data_df)


def extract_boi(row):
    img = np.dstack([get_mat(row['latitude'], row['longitude'], fn)for fn in row['files']])
    with open(OUT_DIR+"%.6d.npy"%row.name, "wb") as f:
        np.save(f, img)


    
    
suomi[:1000].parallel_apply(extract_boi, axis=1)
