import logging

import dateutil
import flask

from .measurements import (
    available_grids,
    available_grid_infos,
    available_grid_measurements
)

from .measurements import (
    available_stations,
    available_stations_per_quantity,
    available_station_infos,
    available_station_measurements
)


logger = logging.getLogger(__name__)


def grids() -> list:
    return available_grids


def grid_info(id) -> list:
    id = str(id)
    data_dir = flask.current_app.config["%s_DATA_DIR" % (id.upper(), )]
    fun = available_grid_infos[id]
    return fun(data_dir)


def grid_measurements(id, quantity, lat, lon, start_time, end_time) -> list:
    id = str(id)
    quantity = str(quantity)
    lat = float(lat)
    lon = float(lon)
    start_time = dateutil.parser.parse(start_time)
    end_time = dateutil.parser.parse(end_time)

    fun = available_grid_measurements[str(id)]
    # get the data directory from the configuration
    data_dir = flask.current_app.config["%s_DATA_DIR" % (str(id).upper(), )]
    records = fun(
        quantity=quantity,
        lat=lat,
        lon=lon,
        start_time=start_time,
        end_time=end_time,
        data_dir=data_dir
    )
    return records


def stations() -> list:
    return available_stations


def stations_per_quantity(dataset, quantity) -> list:
    """return a list of all stations"""
    # concatenate a list of all stations
    dataset = str(dataset)
    quantity = str(quantity)

    fun = available_stations_per_quantity[dataset]
    feature_collection = fun(quantity)
    features = feature_collection.features
    for feature in features:
        feature.properties['dataset'] = dataset
    return feature_collection


def station_info(dataset, id) -> object:
    fun = available_station_infos[dataset]
    station_info = fun(id)
    return station_info


# api conforms to swagger capitalization
def station_measurements(dataset, id, quantity, start_time=None, end_time=None) -> str:
    dataset = str(dataset)
    id = str(id)
    quantity = str(quantity)
    start_time = dateutil.parser.parse(start_time)
    end_time = dateutil.parser.parse(end_time)

    """return measurements for a quantity"""
    fun = available_station_measurements[dataset]
    station_data = fun(id, quantity, start_time=start_time, end_time=end_time)
    return station_data
