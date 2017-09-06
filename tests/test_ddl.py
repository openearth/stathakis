import dateutil.parser

from stathakis.measurements import ddl


def test_metadata():
    metadata = ddl.get_metadata()
    assert metadata['Succesvol'], "we should have a positive response"
    metadata_df = ddl.metadata2df(metadata)
    assert len(metadata_df) > 10, "we should have at least 10 records, got %s" % (list(metadata_df))


def test_get_data():
    station = 'HOEKVHLD'
    start_time = dateutil.parser.parse("2017-3-10T09:00:00.000+01:00")
    end_time = dateutil.parser.parse("2017-3-14T10:10:00.000+01:00")
    quantity = 'waterlevel'
    ddl_data = ddl.get_data(station, quantity, start_time, end_time)
    assert set(ddl_data.keys()) == {'series'}, "we should have a series"


def test_stations():
    quantity = 'waterlevel'
    ddl_data = ddl.get_stations_per_quantity(quantity)
    assert len(ddl_data['features']) >= 10, "we should have at least 10 records"
