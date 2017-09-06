all: ddl_locations.json ddl_locations_realtime.json
# location data for archive data
ddl_locations.json:
	ogr2ogr -t_srs EPSG:4326 -f geojson ddl_locations.json 'WFS:https://waterwebservices.rijkswaterstaat.nl/services/distributielaagWFS/distributielaag_dbo' locaties
# location data for realtime data
ddl_locations_realtime.json:
	ogr2ogr -t_srs EPSG:4326 -f geojson ddl_locations_realtime.json 'WFS:https://waterwebservices.rijkswaterstaat.nl/services/distributielaagWFS/distributielaag_dbo' locatiesmetlaatstewaarneming
