import json
import geojson
import simplejson


def df2geojson(df):
    """convert a dataframe to a geojson object"""
    def row2feature(row):
        properties = row.to_dict()
        geometry = row.point
        feature = geojson.Feature(id=row.name, geometry=geometry, properties=properties)
        return feature
    features = df.apply(row2feature, axis=1).values
    fc = geojson.FeatureCollection(features)
    return fc


class CustomEncoder(simplejson.JSONEncoder):
    """Support for data types that JSON default encoder
    does not do.

    This includes:

        * Numpy array or number
        * Pandas Timestamp
        * Pandas DataFrame
        * geojson types
        * Complex number
        * Set
        * Bytes (Python 3)

    Examples
    --------
    >>> import json
    >>> import numpy as np
    >>> json.dumps(np.arange(3), cls=CustomEncoder)
    '[0, 1, 2]'

    """

    def default(self, obj):
        # try and import everything
        HAVE_NUMPY = False
        try:
            import numpy as np
            HAVE_NUMPY = True
        except ImportError:
            pass
        HAVE_PANDAS = False
        try:
            import pandas as pd
            HAVE_PANDAS = True
        except ImportError:
            pass
        HAVE_GEOJSON = False
        try:
            import geojson
            HAVE_GEOJSON = True
        except ImportError:
            pass

        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):  # pragma: py3
            return obj.decode()
        if HAVE_NUMPY:
            if isinstance(obj, (np.ndarray, np.number)):
                return obj.tolist()
            elif isinstance(obj, (complex, np.complex)):
                return [obj.real, obj.imag]
        if HAVE_PANDAS:
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
        if HAVE_GEOJSON:
            return geojson.GeoJSONEncoder.default(self, obj)
        return simplejson.JSONEncoder.default(self, obj)
