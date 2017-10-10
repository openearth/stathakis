import logging
import pathlib
import json

import netCDF4
import numpy as np
import pandas as pd

from ..utils import CustomEncoder

logger = logging.getLogger(__name__)


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


def get_grid_info(data_dir):
    info = {}
    data_dir = pathlib.Path(data_dir)
    v_urls = list(sorted(data_dir.glob('vwnd.10m.gauss.*.nc')))
    u_urls = list(sorted(data_dir.glob('uwnd.10m.gauss.*.nc')))
    info['urls'] = u_urls + v_urls
    with netCDF4.MFDataset(u_urls, aggdim='time') as ds_u:
        attrs = ds_u.ncattrs()
        for attr in attrs:
            info[attr] = getattr(ds_u, attr)
    with netCDF4.MFDataset(v_urls, aggdim='time') as ds_v:
        attrs = ds_v.ncattrs()
        for attr in attrs:
            info[attr] = getattr(ds_v, attr)
    return info


def get_measurements(data_dir, quantity, lat, lon, start_time, end_time):
    """return data for a given location"""

    data_dir = pathlib.Path(data_dir)
    v_urls = list(sorted(data_dir.glob('vwnd.10m.gauss.*.nc')))
    u_urls = list(sorted(data_dir.glob('uwnd.10m.gauss.*.nc')))

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

    # slice
    s = np.s_[t_start_idx:t_end_idx, lat_idx, lon_idx]

    names = {}
    units = {}
    with netCDF4.MFDataset(u_urls, aggdim='time') as ds_u:
        data['u'] = ds_u.variables['uwnd'][s]
        names['u'] = ds_u.variables['uwnd'].long_name
        units['u'] = ds_u.variables['uwnd'].units
    with netCDF4.MFDataset(v_urls, aggdim='time') as ds_v:
        data['v'] = ds_v.variables['vwnd'][s]
        names['v'] = ds_u.variables['uwnd'].long_name
        units['v'] = ds_u.variables['uwnd'].units

    series = [
        {
            "data": pd.DataFrame(data=dict(
                dateTime=data['t'][t_start_idx:t_end_idx],
                value=data['u']
            )),
            "name": names['u'],
            "units": units['u']
        },
        {
            "data": pd.DataFrame(data=dict(
                dateTime=data['t'][t_start_idx:t_end_idx],
                value=data['v']
            )),
            "name": names['v'],
            "units": units['v']
        }

    ]
    # make sure we serialize to json
    series = json.loads(json.dumps(series, cls=CustomEncoder))
    response = {
        "series": series
    }
    return response
