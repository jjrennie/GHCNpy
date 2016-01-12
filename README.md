# GHCNpy: Weather Station Analysis in Python

GHCNpy pulls in data from the Global Historical Climatology Network - Daily Database. Analysis and visualizations are also made

Background
------------

The Global Historical Climatology Network – Daily data set (GHCN-D) provides a strong foundation of the Earth's climate on the
daily scale, and is the official archive of daily weather data in the United States. The data set is updated nightly, with new data 
ingested with a lag of approximately one day. The data set adheres to a strict set of quality assurance, and lays the foundation 
for other products distributed at the [National Centers for Environmental Information](https://www.ncdc.noaa.gov), 
including the 1981-2010 US Normals.

GHCN-Daily comprises of nearly 100,000 stations globally, and includes over 50 different elements. The CORE elements are as follows:

- TMAX = Daily Maximum Temperature

- TMIN = Daily Maximum Temperature

- TAVG = Daily Average Temperature

- PRCP = Daily Precipitation

- SNOW = Daily Snowfall 

- SNWD = Daily Snow Depth

While a very popular data set, GHCN-Daily is only available in ASCII text or comma separated files, and very little visualization 
is provided to the end user. It makes sense then to build a suite of algorithms that will not only take advantage of its spatial 
and temporal completeness, but also help end users analyze this data in a simple, efficient manner. To that end, a Python package 
has been developed called GHCNpy to address these needs. Open sourced, GHCNpy uses basic packages such as NumPy and 
matplotlib to perform a variety of tasks. Routines include converting the data to CF compliant netCDF files, 
time series analysis, and visualization of data, from the station to global scale. 

More Information about GHCN-Daily can be found [here.](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/)

Installing GHCNpy
------------

GHCNpy should work on Windows, Mac OSX and Linux, however has only been tested in Mac OSX and Linux environments. The code was developed
using the Python 2.7 Anaconda Python Distribution from Continuum Analytics. The Anaconda Python Distribution can be downloaded here: https://store.continuum.io/cshop/anaconda/

Other methods may work (i.e. Macports, built in Python, etc), but has not been tested. Any issues can be reported through contact information below.

__Required Python Packages/Libraries:__

- NumPy

- netCDF4

- GeoPy

- requests

- matplotlib

If these packages are not installed on your system, they will need to be installed. Using Anaconda, this comand can be used:

    conda install *name of package*

Once the packages are installed, you're ready to install GHCNpy. Using git: 

    git clone https://github.com/jjrennie/GHCNpy.git
    
Once the package has been downloaded to your computer you can setup using this command:

    python setup.py install

After installing the package, you can test by using this command:

    python test.py

You are now ready to go!

Functions
------------
There are three major programs used in GHCNpy. It was split up to generalize the three major objects of this package

__io.py (Input/Output of Data):__

Get GHCN-D Version

    get_ghcnd_version()
    
Get GHCN-D Data (Station Text File)

    get_data_station(station_id)
    station_id = GHCN-D 12-digit id
    
Get GHCN-D Data (Year Comma Delimited File)

    get_data_year(year)
    year = Input Year

Get GHCN-D Metadata file (ghcnd-stations.txt)

    get_ghcnd_stations()
    
Get GHCN-D Inventory file (ghcnd-inventory.txt)

    get_ghcnd_inventory()
    
Output to CSV file

    output_to_csv(station_id)
    station_id = GHCN-D 12-digit id

Output to CF compliant netCDF file

    output_to_netcdf(station_id)
    station_id = GHCN-D 12-digit id
    
__metadata.py (Get information about the data):__

Search for a station in GHCN-D

    find_station(*args)
    1 Argument: Search By Name
    3 Arguments: Search by lat/lon/distance limit

Get Metadata of a station in GHCN-D, using both the metadata file, and the Historical Observing Metadata Repository (HOMR).

The result are the following metadata information (if available): Station Latitude, Station Longitude, Station Name, Station Elevation (meters), US State, Climate Division, US County, National Weather Service Office, COOP ID, WBAN ID

    get_metadata(station_id)
    station_id = GHCN-D 12-digit id
    
__plotting.py (Plot the data):__

Plot Temperature Time Series

This plots "New York Times" style temperature plots. For a givin station and period, plots Raw, Average, and Record TMAX / TMIN for each day. Also highlights record day, where the raw value meets or exceeds the record.

    plot_temperature(station_id,begin_date,end_date)
    station_id = GHCN-D 12-digit id
    begin_date = YYYYMMDD
    end_date - YYYYMMDD
    
Plot Accumulated Precipitation. For the stations period of record, plot each year's accumulated precipitation, along with highlighting the max, min, average and current year.

    plot_precipitation(station_id)
    station_id = GHCN-D 12-digit id

Plot Accumulated Snowfall. Same as precip, but start year in October instead of January

    plot_snowfall(station_id)
    station_id = GHCN-D 12-digit id

Plot Data Spatially for a given date and Element. Able to specify projection, lat/lon boxes, dpi. Special color maps are made depending on element. Only uses GHCN-D CORE elements.

    plot_spatial(year,month,day,element)
    element = TMAX/TMIN/TAVG/PRCP/SNOW/SNWD
    
Special Spatial Plots for derived data. Able to specify projection, lat/lon boxes, dpi. Special color maps are made depending on element. Derived data includes heating, cooling, and growing degree days.

    plot_spatial_derived(year,element)
    element = HDD/CDD/GDD
    
Special Spatial Plots for freeze data. Able to specify projection, lat/lon boxes, dpi. Special color maps are made depending on element. Derived data includes date of last freeze (spring) and date of first freeze (fall).

    plot_spatial_freeze(year,element)
    element = LAST/FIRST
    
Future Plans
------------
This is a very ambitious project, and much more will be added, including (but not limited to): 

- Accessing more of GHCN-Daily elements, an extensive list is found [here.](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt)

- Build upon the visualizations and create more derived products

- Add more scientific calculations

- Incorporate mapping visuals, possibly with GIS or others

- Develop a database of information, instead of constantly pinging FTP

- Clean up code, and work on faster runtimes

Contact
------------
Any questions, comments, bug reports, feature requests, and other inquiries should be sent to jared@cicsnc.org
