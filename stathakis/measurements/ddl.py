import functools
import logging
import json
import datetime

import requests
import numpy as np
import pandas as pd
import osgeo.osr
import geojson
import dateutil.parser
import shapely.geometry
import beaker.cache

from ..utils import CustomEncoder, df2geojson

# set cache settings
beaker.cache.cache_regions.update({
    'short_term': {
        'expire': 60,
        'type': 'memory'
    },
    'long_term': {
        'expire': 1800,
        'type': 'dbm',
        'data_dir': '/tmp',
    }
})

cache = beaker.cache.CacheManager()

WGS84 = osgeo.osr.SpatialReference()
WGS84.ImportFromEPSG(4326)


# mapping from Aquo to cf (based on broken csv file)
# TODO: get from source
AQUO2CF = {
    '%O2': 'fractional_saturation_of_oxygen_in_sea_water',
    'CHLFa': 'concentration_of_chlorophyll_in_sea_water',
    'FLUORCTE': 'sea_water_fluorescence',
    'GELDHD': 'sea_water_electrical_conductivity',
    'GELSHD': 'speed_of_sound_in_sea_water',
    'Hm0': 'sea_surface_wave_significant_height',
    'INSLG': 'downwelling_longwave_radiance_in_air',
    'NH4': 'mass_concentration_of_ammonium_in_sea_water',
    'NO2': 'mass_concentration_of_nitrite_in_sea_water',
    'NO3': 'mass_concentration_of_nitrate_in_sea_water',
    'O2': 'mass_concentration_of_oxygen_in_sea_water',
    'P': 'mass_concentration_of_particulate_bound_phosphorus_in_sea_water',
    'POC': 'mass_concentration_of_particulate_bound_organic_carbon_in_sea_water',
    'Q': 'water_volume_transport_into_sea_water_from_rivers',
    'SALNTT': 'sea_water_salinity',
    'SiO2': 'mass_concentration_of_silicate_in_sea_water',
    'T': 'sea_water_temperature',
    'TOC': 'mass_concentration_of_organic_carbon_in_sea_water',
    'TROEBHD': 'sea_water_turbidity',
    'Th0': 'sea_surface_wave_from_direction',
    'Tm02': 'sea_surface_wind_wave_mean_period_from_variance_spectral_density_second_frequency_moment',
    'WATHTE': 'sea_surface_height',
    'ZICHT': 'secchi_depth_of_sea_water',
    'ZS': 'concentration_of_suspended_matter_in_sea_water',
    'pH': 'sea_water_ph_reported_on_total_scale',
    's_NO3NO2': 'mass_concentration_of_nitrate_and_nitrite_in_sea_water',
    'Fp': 'sea_surface_wave_frequency_at_variance_spectral_density_maximum',
    'H1/3': 'sea_surface_wave_mean_height_of_highest_third',
    'LUCHTDK': 'surface_air_pressure',
    'STROOMRTG': 'sea_water_to_direction',
    'STROOMSHD': 'sea_water_velocity',
    'T1/3': 'sea_surface_wave_mean_period_of_longest_third',
    'TH1/3': 'sea_surface_wave_mean_period_of_highest_third',
    'WATHTBRKD': 'sea_surface_height',
    'WINDRTG': 'wind_to_direction',
    'WINDSHD': 'wind_speed'
}

FILTERS = {
    "WATERLEVEL": ['WATHTBRKD', 'WATHTE'],
    "WIND": ['WINDRTG', 'WINDSHD']
}


class NoDataException(BaseException):
    pass


# this takes 6 seconds, which is much too long, so we cache it
@cache.region('long_term', 'rws')
def get_metadata():
    """extract metadata from ddl"""
    ddl_url = 'https://waterwebservices.rijkswaterstaat.nl/METADATASERVICES_DBO/OphalenCatalogus/'

    request = {
        "CatalogusFilter": {
            "Eenheden": True,
            "Grootheden": True,
            "Hoedanigheden": True
        }
    }
    resp = requests.post(ddl_url, json=request)
    result = resp.json()
    return result


# this function is slow because every record can have a different coordinate system
@cache.region('short_term', 'rws')
def metadata2df(metadata, quantity_filter='WATERLEVEL'):
    """parse ddl data and return a data frame"""
    locaties_df = pd.DataFrame.from_dict(metadata['LocatieLijst'])
    metadata_locaties_df = pd.DataFrame.from_dict(metadata['AquoMetadataLocatieLijst'])
    metadata_df = pd.DataFrame.from_dict(metadata['AquoMetadataLijst'])

    # lowercase all columns (inconsistent)
    # should be in mergeable order
    dfs = [locaties_df, metadata_locaties_df, metadata_df]
    for df in dfs:
        df.columns = [x.lower() for x in df.columns]
    merged_df = functools.reduce(
        lambda left, right: pd.merge(left, right),
        dfs
    )

    # let's hope there's only one coordinate system in use:
    assert len(set(merged_df.coordinatenstelsel)) == 1, 'assuming only 1 coordinate system'
    # get the epsg code
    crs = list(set(merged_df.coordinatenstelsel))[0]
    srs = osgeo.osr.SpatialReference()
    srs.ImportFromEPSG(int(crs))
    srs2wgs84 = osgeo.osr.CoordinateTransformation(srs, WGS84)
    points = srs2wgs84.TransformPoints(np.array(merged_df[['x', 'y']]))
    points = [
        shapely.geometry.Point(pt[0], pt[1])
        for pt
        in points
    ]

    # this is very slow because we check coordinate system for each row
    merged_df['point'] = points
    merged_df['lon'] = merged_df.point.apply(lambda pt: pt.x)
    merged_df['lat'] = merged_df.point.apply(lambda pt: pt.y)

    # flatten some columns
    merged_df['units'] = merged_df.eenheid.apply(lambda x: x['Code'])
    merged_df['quantity'] = merged_df.grootheid.apply(lambda x: x['Code'])

    merged_df['standard_name'] = merged_df.grootheid.apply(lambda x: AQUO2CF.get(x['Code'], ''))
    # only show stations of relevant quantity
    idx = np.in1d(merged_df.quantity, FILTERS['WATERLEVEL'])
    filtered_df = merged_df[idx]
    # TODO:
    # convert to standard names using
    # translation_df = pd.read_csv('../data/deltares/wns_en.csv', sep=';', keep_default_na=False)
    return filtered_df



@cache.region('short_term', 'rws')
def get_series(row, start_time, end_time, validated=False):
    """get timeseries for a given row"""
    station = row

    metadata_url = 'https://waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES_DBO/OphalenWaarnemingen'
    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Grootheid": {
                    "Code": station.grootheid['Code']
                }
            }
        },
        "Locatie": {
            "X": station.x,
            "Y": station.y,
            "Code": station.code
        },
        "Periode": {
            "Begindatumtijd": start_time,
            "Einddatumtijd": end_time
        }
    }
    resp = requests.post(metadata_url, json=request)
    data = resp.json()
    if not data['Succesvol']:
        raise NoDataException(data['Foutmelding'])
    measurements = []
    metadata = {}
    for row in data['WaarnemingenLijst']:
        # metadata is specified per row, just update it so we have 1
        metadata.update(row['AquoMetadata'])
        standard_name = AQUO2CF.get(row['AquoMetadata']['Grootheid']['Code'])
        metadata['standard_name'] = standard_name
        metadata.update(row['Locatie'])
        for measurement in row['MetingenLijst']:
            # only add validated data if requested
            if validated and 'Gecontroleerd' not in measurement['WaarnemingMetadata']['StatuswaardeLijst']:
                continue
            measurements.append(measurement)

    timeseries = []
    for measurement in measurements:
        record = {}
        record['v'] = measurement['Meetwaarde']['Waarde_Numeriek']
        UTC = dateutil.tz.tzutc()
        # parse time
        date = dateutil.parser.parse(measurement['Tijdstip'])
        # convert to UTC
        record['t'] = date.astimezone(UTC)
        timeseries.append(record)
    timeseries_df = pd.DataFrame(timeseries)
    series = timeseries_df
    return {
        "timeseries": series,
        "metadata": metadata
    }


def get_data(station, start_time, end_time):
    """get data for station"""
    metadata = get_metadata()
    metadata_df = metadata2df(metadata)

    datasets = []
    available_series = metadata_df[metadata_df.code == station]
    for idx, row in available_series.iterrows():
        try:
            series = get_series(row, start_time, end_time)
        except NoDataException as e:
            logging.exception('no data for %s at %s', row.quantity, row.code)
            continue
        datasets.append(series)
    return datasets


@cache.region('short_term', 'rws')
def get_metadata_response():
    metadata = get_metadata()
    metadata_df = metadata2df(metadata)
    fc = df2geojson(metadata_df)
    # serializa/deserialize to get rid of custom types
    response = json.loads(geojson.dumps(fc, cls=CustomEncoder))
    return response


@cache.region('short_term', 'rws')
def get_matadata_resposne(station, start_time=None, end_time=None):
    now = datetime.datetime.now()
    two_days = datetime.timedelta(days=2)
    if start_time is None:
        start_time = (now - two_days).isoformat()
    if end_time is None:
        end_time = (now + two_days).isoformat()
    data = get_data()
    response = json.loads(geojson.dumps(data, cls=CustomEncoder))
    return response
