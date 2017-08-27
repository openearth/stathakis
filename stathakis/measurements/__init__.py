from .ncep import get_measurements

available_grids = {
    "ncep": get_measurements
}

__all__ = ['available_grids']
