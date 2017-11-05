all: vwnd.10m.gauss.2017.nc uwnd.10m.gauss.2017.nc
uwnd.10m.gauss.2017.nc:
	wget -c -nd -r --accept='*uwnd.10m.gauss.201[01].nc' ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/surface_gauss/
# ncrcat uwnd.10m.gauss.????.nc uwnd.10m.gauss.nc
vwnd.10m.gauss.2017.nc:
	wget -c -nd -r --accept='*vwnd.10m.gauss.201[01].nc' ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/surface_gauss/
#ncrcat vwnd.10m.gauss.????.nc vwnd.10m.gauss.nc
