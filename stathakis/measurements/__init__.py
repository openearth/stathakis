from .ncep import get_measurements
from .ddl import get_stations

available_grids = {
    "ncep": get_measurements
}
available_stations = {
    "rws": get_stations
}

__all__ = ['available_grids', 'available_stations']
