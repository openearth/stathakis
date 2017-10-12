# config defaults
import pathlib

if pathlib.Path('/data/noaa').exists():
    NCEP_DATA_DIR = '/data/noaa/ncep'
else:
    NCEP_DATA_DIR = 'data/noaa/ncep'
