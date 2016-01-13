# Import Modules
import numpy as np
from ftplib import FTP
import ghcnpy as gp
import datetime
from datetime import date
import netCDF4 as nc
import re
import os.path
import sys

#################################################
# MODULE: get_ghcnd_version
# Get which version of GHCN-D we are using
#################################################
def get_ghcnd_version():

  ftp = FTP('ftp.ncdc.noaa.gov')
  ftp.login()
  ftp.cwd('pub/data/ghcn/daily')
  ftp.retrbinary('RETR ghcnd-version.txt', open('ghcnd-version.txt', 'wb').write)
  ftp.quit()

  ghcnd_versionfile='ghcnd-version.txt'
  try:
    with open (ghcnd_versionfile, "r") as myfile:
        ghcnd_version=myfile.read().replace('\n', '')
  except:
    print("Version file does not exist: ",ghcnd_versionfile)
    sys.exit()

  return ghcnd_version

#################################################
# MODULE: get_data_station
# Fetch Individual station (.dly ASCII format)
#################################################
def get_data_station(station_id):
  print("\nGETTING DATA FOR STATION: ",station_id)

  ftp = FTP('ftp.ncdc.noaa.gov')
  ftp.login()
  ftp.cwd('pub/data/ghcn/daily/all')
  ftp.retrbinary('RETR '+station_id+'.dly', open(station_id+'.dly', 'wb').write)
  ftp.quit()

  outfile=station_id+".dly"
  return outfile

#################################################
# MODULE: get_data_year
# Fetch 1 Year of Data (.csv ASCII format)
#################################################
def get_data_year(year):
  print("\nGETTING DATA FOR YEAR: ",year)

  ftp = FTP('ftp.ncdc.noaa.gov')
  ftp.login()
  ftp.cwd('pub/data/ghcn/daily/by_year')
  ftp.retrbinary('RETR '+year+'.csv.gz', open(year+'.csv.gz', 'wb').write)
  ftp.quit()

  outfile=year+".csv.gz"
  return outfile

#################################################
# MODULE: get_ghcnd_stations
# Get ghcnd-stations.txt file
#################################################
def get_ghcnd_stations():
  print("\nGRABBING LATEST STATION METADATA FILE")

  ftp = FTP('ftp.ncdc.noaa.gov')
  ftp.login()
  ftp.cwd('pub/data/ghcn/daily')
  ftp.retrbinary('RETR ghcnd-stations.txt', open('ghcnd-stations.txt', 'wb').write)
  ftp.quit()

  # Read in GHCND-D Stations File
  ghcnd_stnfile='ghcnd-stations.txt'
  ghcnd_stations= np.genfromtxt(ghcnd_stnfile,delimiter=(11,9,10,7,4,30),dtype=str)

  return ghcnd_stations

#################################################
# MODULE: get_ghcnd_inventory
# Get ghcnd-stations.txt file
#################################################
def get_ghcnd_inventory():
  print("\nGRABBING LATEST STATION INVENTORY FILE")

  ftp = FTP('ftp.ncdc.noaa.gov')
  ftp.login()
  ftp.cwd('pub/data/ghcn/daily')
  ftp.retrbinary('RETR ghcnd-inventory.txt', open('ghcnd-inventory.txt', 'wb').write)
  ftp.quit()

  # Read in GHCND-D INVENTORY File
  ghcnd_invfile='ghcnd-inventory.txt'
  ghcnd_inventory= np.genfromtxt(ghcnd_invfile,delimiter=(11,9,11,4),dtype=str)

  return ghcnd_inventory

#################################################
# MODULE: output_to_csv
# Output to csv (one station per csv)
#################################################
def output_to_csv(station_id):
  print("\nOUTPUTTING TO CSV: ",station_id,".csv")

  # 5 Elements of GHCN-D
  num_elements=5
  tmax=0
  tmin=1
  prcp=2
  snow=3
  snwd=4

  # Grab Data
  gp.get_data_station(station_id)

  # Read in GHCN-D Data
  infile = station_id+".dly"

  file_handle = open(infile, 'r')
  ghcnd_contents = file_handle.readlines()
  file_handle.close()

  # Get Year Start and End of File for time dimensions
  ghcnd_begin_year =  int(ghcnd_contents[0][11:15])
  ghcnd_end_year = int(ghcnd_contents[len(ghcnd_contents)-1][11:15])
  num_years = int((ghcnd_end_year - ghcnd_begin_year) + 1)

  # Go through GHCN-D Data
  ghcnd_data= np.zeros((num_years,12,31,num_elements),dtype='f')-(9999.0)

  for counter in xrange(len(ghcnd_contents)):
    element = ghcnd_contents[counter][17:21]

    if element == "TMAX" or element == "TMIN" or element == "PRCP" or element == "SNOW" or element == "SNWD":
      if element == "TMAX":
        element_counter=tmax
        divisor = 10.0
      if element == "TMIN":
        element_counter=tmin
        divisor = 10.0
      if element == "PRCP":
        element_counter=prcp
        divisor = 10.0
      if element == "SNOW":
        element_counter=snow
        divisor = 1.0
      if element == "SNWD":
        element_counter=snwd
        divisor = 1.0

      year = int(ghcnd_contents[counter][11:15])
      year_counter = int(year - ghcnd_begin_year)
      month = int(ghcnd_contents[counter][15:17])
      month_counter = int(month - 1)

      char=21
      for day_counter in xrange(0,31):
        if ghcnd_contents[counter][char:char+5] != "-9999" and ghcnd_contents[counter][char+6:char+7].strip() == "":
          ghcnd_data[year_counter,month_counter,day_counter,element_counter] = float(ghcnd_contents[counter][char:char+5]) / divisor
        char = char + 8

  # Print(out data to csv file)
  outfile_data = station_id+'.csv'
  out_data = open(outfile_data,'w')
  out_data.write("YYYY,MM,DD,TMAX,TMIN,PRCP,SNOW,SNWD\n")
  for year_counter in xrange(0,num_years):
    for month_counter in xrange(0,12):
      for day_counter in xrange(0,31):

        # Print(Out)
        if (ghcnd_data[year_counter,month_counter,day_counter,tmax] != -9999. or \
            ghcnd_data[year_counter,month_counter,day_counter,tmin] != -9999. or \
            ghcnd_data[year_counter,month_counter,day_counter,prcp] != -9999. or \
            ghcnd_data[year_counter,month_counter,day_counter,snow] != -9999. or \
            ghcnd_data[year_counter,month_counter,day_counter,snwd] != -9999.):
          out_data.write("%04i,%02i,%02i,%7.1f,%7.1f,%7.1f,%7.1f,%7.1f\n" % \
                   (year_counter+ghcnd_begin_year,month_counter+1,day_counter+1,\
                   ghcnd_data[year_counter,month_counter,day_counter,tmax],\
                   ghcnd_data[year_counter,month_counter,day_counter,tmin],\
                   ghcnd_data[year_counter,month_counter,day_counter,prcp],\
                   ghcnd_data[year_counter,month_counter,day_counter,snow],\
                   ghcnd_data[year_counter,month_counter,day_counter,snwd]))
  out_data.close()
  return None

#################################################
# MODULE: output_to_netcdf
# Output to netcdf (one station per netcDF)
#################################################
def output_to_netcdf(station_id):
  print("\nOUTPUTTING TO netCDF: ",station_id,".nc")

  begin_year=1700
  end_year=datetime.datetime.now().year
  num_years=(end_year-begin_year) + 1

  start_date=date(begin_year, 1, 1)
  end_date=date(end_year,12,31)

  # 5 Elements of GHCN-D
  num_elements=5
  tmax=0
  tmin=1
  prcp=2
  snow=3
  snwd=4

  # 3 Flags for each value
  num_flags=3

  # Measurement Flag (MFLAG)
  mflag=0
  mflag_codes = np.array([ord(x) for x in ["B","D","H","K","L","O","P","T","W"]],dtype='b')
  mflag_meanings = np.array(["precipitation total formed from two 12 hour totals".replace(" ","_")+" ",\
                             "precipitation total formed from four six hour totals".replace(" ","_")+" ",\
                             "represents highest or lowest hourly temperature".replace(" ","_")+" ",\
                             "converted from knots".replace(" ","_")+" ",\
                             "temperature appears to be lagged with respect to reported hour of observation".replace(" ","_")+" ",\
                             "converted from oktas".replace(" ","_")+" ",\
                             "identified as missing presumed zero in DSI 3200 and 3206".replace(" ","_")+" ",\
                             "trace of precipitation snowfall or snow depth".replace(" ","_")+" ",\
                             "converted from 16 point WBAN code for wind direction".replace(" ","_")],\
                             dtype='str')

  # Quality Control Flag (QCFLAG)
  qcflag=1
  qcflag_codes = np.array([ord(x) for x in ["D","G","I","K","L","M","N","O","R","S","T","W","X","Z"]],dtype='b')
  qcflag_meanings = np.array(["failed duplicate check".replace(" ","_")+" ",\
                              "failed gap check".replace(" ","_")+" ",\
                              "failed internal consistency check".replace(" ","_")+" ",\
                              "failed streak frequent value check".replace(" ","_")+" ",\
                              "failed check on length of multiday period".replace(" ","_")+" ",\
                              "failed megaconsistency check".replace(" ","_")+" ",\
                              "failed naught check".replace(" ","_")+" ",\
                              "failed climatological outlier check".replace(" ","_")+" ",\
                              "failed lagged range check".replace(" ","_")+" ",\
                              "failed spatial consistency check".replace(" ","_")+" ",\
                              "failed temporal consistency check".replace(" ","_")+" ",\
                              "failed bounds check".replace(" ","_")+" ",\
                              "failed climatological outlier check".replace(" ","_")+" ",\
                              "flagged as a result of an official Datzilla investigation".replace(" ","_")],\
                              dtype='str')

  # Source Flag (SRCFLAG)
  srcflag=2
  srcflag_codes = np.array([ord(x) for x in ["0","6","7","A","a","B","b","C","E","F","G","H","I","K","M","N","Q","R","r","S","s",\
                                             "T","U","u","W","X","Z","z"]],dtype='b')
  srcflag_meanings = np.array(["US Cooperative Summary of the Day".replace(" ","_")+" ",\
                               "CDMP Cooperative Summary of the Day".replace(" ","_")+" ",\
                               "US Cooperative Summary of the Day Transmitted via WxCoder3".replace(" ","_")+" ",\
                               "Automated Surface Observing System real time data since January 1 2006".replace(" ","_")+" ",\
                               "Australian data from the Australian Bureau of Meteorology".replace(" ","_")+" ",\
                               "US ASOS data for October 2000 to December 2005".replace(" ","_")+" ",\
                               "Belarus update".replace(" ","_")+" ",\
                               "Environment Canada".replace(" ","_")+" ",\
                               "European Climate Assessment and Dataset".replace(" ","_")+" ",\
                               "US Fort data".replace(" ","_")+" ",\
                               "Official Global Climate Observing System".replace(" ","_")+" ",\
                               "High Plains Regional Climate Center real time data".replace(" ","_")+" ",\
                               "International collection non U.S. data received through personal contacts".replace(" ","_")+" ",\
                               "US Cooperative Summary of the Day data digitized from paper observer forms".replace(" ","_")+" ",\
                               "Monthly METAR Extract".replace(" ","_")+" ",\
                               "Community Collaborative Rain Hail and Snow".replace(" ","_")+" ",\
                               "Data from several African countries that had been quarantined".replace(" ","_")+" ",\
                               "Climate Reference Network and Historical Climatology Network Modernized".replace(" ","_")+" ",\
                               "All Russian Research Institute of Hydrometeorological Information World Data Center".replace(" ","_")+" ",\
                               "Global Summary of the Day".replace(" ","_")+" ",\
                               "China Meteorological Administration National Meteorological Information Center".replace(" ","_")+" ",\
                               "SNOwpack TELemtry data obtained from the Western Regional Climate Center".replace(" ","_")+" ",\
                               "Remote Automatic Weather Station data obtained from the Western Regional Climate Center".replace(" ","_")+" ",\
                               "Ukraine update".replace(" ","_")+" ",\
                               "WBAN ASOS Summary of the Day from Integrated Surface Data ISD".replace(" ","_")+" ",\
                               "US First Order Summary of the Day".replace(" ","_")+" ",\
                               "Datzilla official additions or replacements".replace(" ","_")+" ",\
                               "Uzbekistan update ".replace(" ","_")],\
                            dtype='str')



  # Get Version Number of GHCN-D
  ghcnd_version=gp.get_ghcnd_version()

  # Grab Data
  gp.get_data_station(station_id)

  # Read in GHCN-D Data
  infile = station_id+".dly"

  file_handle = open(infile, 'r')
  ghcnd_contents = file_handle.readlines()
  file_handle.close()

  # Get Year Start and End of File for time dimensions
  station_start_year =  int(ghcnd_contents[0][11:15])
  station_end_year = int(ghcnd_contents[len(ghcnd_contents)-1][11:15])
  station_start_month =  int(ghcnd_contents[0][15:17])
  station_end_month = int(ghcnd_contents[len(ghcnd_contents)-1][15:17])

  num_values=0
  results_time = np.zeros((num_years*12*31),dtype='f')-(9999.0)
  results_pos = np.zeros((num_years,12,31),dtype='f')-(9999.0)
  for year in xrange(station_start_year,station_end_year+1):
    year_counter = int(year - station_start_year)

    if year == station_start_year:
      begin_month = int(station_start_month-1)
    else:
      begin_month = 0

    if year == station_end_year:
      end_month = int(station_end_month)
    else:
      end_month = 12

    for month_counter in xrange(begin_month,end_month):
      month = month_counter + 1
      for day_counter in xrange(0,31):
        day = day_counter + 1
        try:
          current_date=date(year,month,day)
          num_days = (current_date-start_date).days
          results_time[num_values] = num_days
          results_pos[year_counter,month_counter,day_counter] = int(num_values)
          num_values+=1
        except:
          pass

  #################################################
  # Open netCDF file
  outfile=station_id+'.nc'
  test=os.path.exists(outfile)
  if test == True:
    os.remove(outfile)
  output = nc.Dataset(outfile, mode='w')

  #################################################
  # Create global attributes
  output.title = "Global Historical Climatology Network - Daily Dataset"
  output.summary = "GHCN-Daily is an integrated database of daily climate summaries from land surface stations across the globe. "+\
                   "GHCN-Daily is comprised of daily climate records from numerous sources that have been integrated and "+\
                   "subjected to a common suite of quality assurance reviews. This dataset includes the top five core elements: "+\
                   "PRCP (precipitation), SNOW (snowfall), SNWD (snow depth), TMAX (maximum temperature), TMIN (minimum temperature)"
  output.version=ghcnd_version
  output.keywords = "daily, station, extremes, temperature, precipitation, snowfall, snow depth"
  output.Conventions = "CF-1.6, ACDD-1.3"
  output.institution = "Cooperative Institute for Climate and Satellites - North Carolina (CICS-NC) and "+\
                       "NOAAs National Centers for Environmental Information (NCEI), Asheville, North Carolina, USA"
  output.source = "surface observations from multiple sources around the globe"
  output.featureType = "timeSeries"
  output.history = "File generatred on ",str(datetime.datetime.now())
  output.creator_name = "Jared Rennie, CICS-NC"
  output.creator_email = "jared@cicsnc.org"
  output.creator_url = "http://www.cicsnc.org/people/jared-rennie/"
  output.references= "Menne et al 2012: http://dx.doi.org/10.1175/JTECH-D-11-00103.1"
  output.comment="More information can be found here: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt"

  #################################################
  # Create Dimensions
  output.createDimension('element',num_elements)
  output.createDimension('time',num_values)
  output.createDimension('name_strlen',30)
  output.createDimension('id_strlen',11)

  #################################################
  # Create Variables

  # LON
  lon_var = output.createVariable('lon', datatype='f')
  lon_var.standard_name = "longitude"
  lon_var.long_name = "station longitude"
  lon_var.units = "degrees_east"

  # LAT
  lat_var = output.createVariable('lat', datatype='f')
  lat_var.standard_name = "latitude"
  lat_var.long_name = "station latitude"
  lat_var.units = "degrees_north"

  # ELEV (ALT)
  alt_var = output.createVariable('alt', datatype='f')
  alt_var.long_name = "vertical distance above the surface"
  alt_var.standard_name = "height"
  alt_var.units = "m"
  alt_var.positive = "up"
  alt_var.axis = "Z"

  # ID
  id_var = output.createVariable('id', datatype='S1', dimensions=('id_strlen'))
  id_var.long_name = "station identifier"

  # NAME
  name_var = output.createVariable('station_name', datatype='S1', dimensions=('name_strlen'))
  name_var.long_name = "station name"
  name_var.cf_role = "timeseries_id"

  # TIME
  time_var = output.createVariable('time', datatype='f8', dimensions='time')
  time_var.standard_name = "time"
  time_var.long_name = "Time of Measurement"
  time_var.units = "days since ",begin_year,"-01-01 00:00:00"
  time_var.calendar = "gregorian"
  time_var.axis = "T"
  time_var[:] = results_time[0:num_values]
  time_var.valid_min = np.min(results_time[0:num_values])

  # FLAGS
  mflag_var = output.createVariable('mflag', datatype='b', dimensions=('time','element'), fill_value=32.)
  mflag_var.long_name = "measurement flag"
  mflag_var.flag_values=mflag_codes
  mflag_var.flag_meanings=mflag_meanings

  qcflag_var = output.createVariable('qcflag', datatype='b', dimensions=('time','element'), fill_value=32.)
  qcflag_var.long_name = "quality control flag"
  qcflag_var.flag_values=qcflag_codes
  qcflag_var.flag_meanings=qcflag_meanings

  srcflag_var = output.createVariable('srcflag', datatype='b', dimensions=('time','element'), fill_value=32.)
  srcflag_var.long_name = "source flag"
  srcflag_var.flag_values=srcflag_codes
  srcflag_var.flag_meanings=srcflag_meanings

  # TMAX
  tmax_var = output.createVariable('tmax', datatype='f', dimensions=('time'), fill_value=-9999.)
  tmax_var.long_name = "surface maximum temperature"
  tmax_var.units = "Celsius"
  tmax_var.coordinates = "time lat lon alt station_name"
  tmax_var.ancillary_variables = "mflag qcflag srcflag"

  # TMIN
  tmin_var = output.createVariable('tmin', datatype='f', dimensions=('time'), fill_value=-9999.)
  tmin_var.long_name = "surface minimum temperature"
  tmin_var.units = "Celsius"
  tmin_var.coordinates = "time lat lon alt station_name"
  tmin_var.ancillary_variables = "mflag qcflag srcflag"

  # PRCP
  prcp_var = output.createVariable('prcp', datatype='f', dimensions=('time'), fill_value=-9999.)
  prcp_var.long_name = "surface precipitation"
  prcp_var.units = "mm"
  prcp_var.coordinates = "time lat lon alt station_name"
  prcp_var.ancillary_variables = "mflag qcflag srcflag"

  # SNOW
  snow_var = output.createVariable('snow', datatype='f', dimensions=('time'), fill_value=-9999.)
  snow_var.long_name = "surface snowfall"
  snow_var.units = "mm"
  snow_var.coordinates = "time lat lon alt station_name"
  snow_var.ancillary_variables = "mflag qcflag srcflag"

  # SNWD
  snwd_var = output.createVariable('snwd', datatype='f', dimensions=('time'), fill_value=-9999.)
  snwd_var.long_name = "surface snow depth"
  snwd_var.units = "mm"
  snwd_var.coordinates = "time lat lon alt station_name"
  snwd_var.ancillary_variables = "mflag qcflag srcflag"

  #################################################
  # Read in GHCN-D Meta
  ghcnd_stations=gp.get_ghcnd_stations()
  ghcnd_meta = ghcnd_stations[ghcnd_stations[:,0] == station_id]

  ghcnd_id=ghcnd_meta[0][0]
  ghcnd_lat=float(ghcnd_meta[0][1])
  ghcnd_lon=float(ghcnd_meta[0][2])
  ghcnd_alt=float(ghcnd_meta[0][3])
  ghcnd_name=ghcnd_meta[0][5]
  ghcnd_name = ghcnd_name.strip()
  ghcnd_name = re.sub(' +',' ',ghcnd_name)
  ghcnd_name = ghcnd_name.replace(" ","_")

  for string_counter in xrange(0,len(ghcnd_id)):
    id_var[string_counter] = ghcnd_id[string_counter]
  lat_var[:] = ghcnd_lat
  lon_var[:] = ghcnd_lon
  alt_var[:] = ghcnd_alt
  for string_counter in xrange(0,len(ghcnd_name)):
    name_var[string_counter] = ghcnd_name[string_counter]

  #################################################
  # Go through GHCN-D Data
  ghcnd_data= np.zeros((num_values,num_elements),dtype='f')-(9999.0)
  ghcnd_flag= np.zeros((num_values,num_elements,num_flags),dtype='i')+32

  for counter in xrange(len(ghcnd_contents)):
    element = ghcnd_contents[counter][17:21]

    if element == "TMAX" or element == "TMIN" or element == "PRCP" or element == "SNOW" or element == "SNWD":
      if element == "TMAX":
        element_counter=tmax
        divisor = 10.0
      if element == "TMIN":
        element_counter=tmin
        divisor = 10.0
      if element == "PRCP":
        element_counter=prcp
        divisor = 10.0
      if element == "SNOW":
        element_counter=snow
        divisor = 1.0
      if element == "SNWD":
        element_counter=snwd
        divisor = 1.0

      year = int(ghcnd_contents[counter][11:15])
      year_counter = int(year - station_start_year)
      month = int(ghcnd_contents[counter][15:17])
      month_counter = int(month - 1)

      char=21
      for day_counter in xrange(0,31):
        time_pos=results_pos[year_counter,month_counter,day_counter]

        # Get Values / Flags
        if ghcnd_contents[counter][char:char+5] != "-9999":
          ghcnd_data[time_pos,element_counter] = float(ghcnd_contents[counter][char:char+5]) / divisor
          ghcnd_flag[time_pos,element_counter,mflag] = ord(ghcnd_contents[counter][char+5:char+6])
          ghcnd_flag[time_pos,element_counter,qcflag] = ord(ghcnd_contents[counter][char+6:char+7])
          ghcnd_flag[time_pos,element_counter,srcflag] = ord(ghcnd_contents[counter][char+7:char+8])
        char = char + 8

  #################################################
  # Assign data to netCDF variables
  tmax_var[:] = ghcnd_data[:,tmax]
  tmax_var.valid_min = np.min(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,tmax,qcflag]!=ord(" "),ghcnd_data[:,tmax]),-9999))
  tmax_var.valid_max = np.max(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,tmax,qcflag]!=ord(" "),ghcnd_data[:,tmax]),-9999))

  tmin_var[:] = ghcnd_data[:,tmin]
  tmin_var.valid_min = np.min(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,tmin,qcflag]!=ord(" "),ghcnd_data[:,tmin]),-9999))
  tmin_var.valid_max = np.max(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,tmin,qcflag]!=ord(" "),ghcnd_data[:,tmin]),-9999))

  prcp_var[:] = ghcnd_data[:,prcp]
  prcp_var.valid_min = np.min(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,prcp,qcflag]!=ord(" "),ghcnd_data[:,prcp]),-9999))
  prcp_var.valid_max = np.max(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,prcp,qcflag]!=ord(" "),ghcnd_data[:,prcp]),-9999))

  snow_var[:] = ghcnd_data[:,snow]
  snow_var.valid_min = np.min(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,snow,qcflag]!=ord(" "),ghcnd_data[:,snow]),-9999))
  snow_var.valid_max = np.max(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,snow,qcflag]!=ord(" "),ghcnd_data[:,snow]),-9999))

  snwd_var[:] = ghcnd_data[:,snwd]
  snwd_var.valid_min = np.min(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,snwd,qcflag]!=ord(" "),ghcnd_data[:,snwd]),-9999))
  snwd_var.valid_max = np.max(np.ma.masked_equal(np.ma.masked_where(ghcnd_flag[:,snwd,qcflag]!=ord(" "),ghcnd_data[:,snwd]),-9999))

  mflag_var[:,:] = ghcnd_flag[:,:,mflag]
  qcflag_var[:,:] = ghcnd_flag[:,:,qcflag]
  srcflag_var[:,:] = ghcnd_flag[:,:,srcflag]

  #################################################
  # Close netCDF file
  output.close()

  return None
