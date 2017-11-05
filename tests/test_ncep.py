import pathlib

import dateutil.parser

from stathakis.measurements import ncep


def test_grid():
    data_dir = pathlib.Path('data/noaa/ncep')
    metadata = ncep.get_grid_info(data_dir)
    assert 'title' in metadata.keys()


def test_get_measurement():
    start_time = dateutil.parser.parse("2010-3-10T09:00:00.000+01:00")
    end_time = dateutil.parser.parse("2010-3-14T10:10:00.000+01:00")
    lat = 52
    lon = 3
    data_dir = pathlib.Path('data/noaa/ncep')
    quantity = 'wind'
    data = ncep.get_measurements(data_dir, quantity, lat, lon, start_time, end_time)
    assert set(data.keys()) == {'series'}, "we should have a series"
