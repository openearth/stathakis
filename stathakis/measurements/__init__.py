from . import ncep
from . import ddl

available_grids = [
    "ncep"
]

available_grid_measurements = {
    "ncep": ncep.get_measurements
}

available_stations = [
    "rws"
]

available_stations_per_quantity = {
    "rws": ddl.get_stations_per_quantity
}

available_station_infos = {
    "rws": ddl.get_station_info
}

available_station_measurements = {
    "rws": ddl.get_station_measurements
}

__all__ = [
    'available_grids',
    'available_stations',
    'available_station_infos',
    'available_station_measurements'
]
