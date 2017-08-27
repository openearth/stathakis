import logging
import pathlib

import netCDF4
import numpy as np
import pandas as pd

import dateutil.parser
# find closest points

logger = logging.getLogger(__name__)




# TODO: configure
data_dir = pathlib.Path('/mnt/efs/data/noaa/ncep')

v_urls = list(sorted(data_dir.glob('vwnd.10m.gauss.*.nc')))
u_urls = list(sorted(data_dir.glob('uwnd.10m.gauss.*.nc')))


def check(u_urls, v_urls):
    """check files for consistency and assumptions"""
    with netCDF4.MFDataset(u_urls, aggdim='time') as ds_u:
        # lookup variables in both files
        t_u = ds_u.variables['time'][:]
        lon_u = ds_u.variables['lon'][:]
        lat_u = ds_u.variables['lat'][:]

    with netCDF4.MFDataset(u_urls, aggdim='time') as ds_v:
        # assert equality
        t_v = ds_v.variables['time'][:]
        lon_v = ds_v.variables['lon'][:]
        lat_v = ds_v.variables['lat'][:]
    assert (t_u == t_v).all()
    assert (lat_u == lat_v).all()
    assert (lon_u == lon_v).all()
    # assert assumed units
    assert ds_u.variables['time'].units == 'hours since 1800-01-01 00:00:0.0'
    assert ds_v.variables['time'].units == 'hours since 1800-01-01 00:00:0.0'


# get all data required to find correct dataset
data = {}
with netCDF4.MFDataset(u_urls, aggdim='time') as ds_u:
    # lookup variables in both files
    t_u = ds_u.variables['time'][:]
    lon_u = ds_u.variables['lon'][:]
    lat_u = ds_u.variables['lat'][:]


# don't use num2date from netcdf4, too slow
t0 = np.datetime64('1800-01-01', 'm')
# use variables from u
data['t'] = t0 + t_u.astype('timedelta64[h]')
data['lon'] = lon_u
data['lat'] = lat_u
lat_idx = np.argmin(np.abs(data['lat'] - lat))
lon_idx = np.argmin(np.abs(data['lon'] - lon))
data['lat'][lat_idx], data['lon'][lon_idx], (lat_idx, lon_idx)
t_range = np.asarray([start_time, end_time], 'datetime64[m]')
t_start_idx, t_end_idx = np.searchsorted(data['t'], t_range)
t_start_idx, t_end_idx

with netCDF4.MFDataset(u_urls, aggdim='time') as ds_u:
    data['u'] = ds_u.variables['uwnd'][t_start_idx:t_end_idx, lat_idx, lon_idx]
with netCDF4.MFDataset(v_urls, aggdim='time') as ds_v:
    data['v'] = ds_v.variables['vwnd'][t_start_idx:t_end_idx, lat_idx, lon_idx]


df = pd.DataFrame(data=dict(
    t=data['t'][t_start_idx:t_end_idx],
    u=data['u'],
    v=data['v']
))


response = df.to_json(orient='records')
