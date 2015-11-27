# Import Modules
import numpy as np
import numpy.ma as ma
import sys 
import time
import datetime
import calendar
import re, json
from ftplib import FTP
import requests as r
from calendar import monthrange
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, date
import matplotlib.colors as colors
import pylab
from geopy.distance import great_circle
import ghcnpy as gp

#################################################
# MODULE: find_station
# Find stations by certain Search Criteria
#    1 Arg: Search by Name
#    3 Arg: Search by Lat Lon Distance limit
#################################################
def find_station(*args):
  stns=0
  if len(args) ==1:
    station_name=args[0]
    print "LOOKUP BY STATION NAME: ",station_name          
    ghcnd_stations=gp.get_ghcnd_stations()
    
    stns=filter(lambda x: re.search(station_name,x), ghcnd_stations[:,5])
    print "GHCND ID          LAT        LON    ELEV(m)  ST       STATION NAME"
    print "###############################################################"
    for station_counter in xrange(len(stns)):
      ghcnd_meta = ghcnd_stations[ghcnd_stations[:,5]== stns[station_counter]]
      print ghcnd_meta[0][0],ghcnd_meta[0][1],ghcnd_meta[0][2],ghcnd_meta[0][3],ghcnd_meta[0][4],ghcnd_meta[0][5]
    
  elif len(args)==3:
    station_lat=args[0]
    station_lon=args[1]
    distance_limit=args[2]
    
    print "LOOKUP BY STATION LAT: ",station_lat," LON: ",station_lon, " DIST LIMIT (mi): ",distance_limit
        
    target_latlon = (float(station_lat), float(station_lon))
    ghcnd_stations=gp.get_ghcnd_stations()
    
    print "GHCND ID          LAT        LON    ELEV(m)  ST       STATION NAME"
    print "###############################################################"
    for ghcnd_counter in xrange(ghcnd_stations[:,0].size): 
      candidate_latlon=(ghcnd_stations[ghcnd_counter][1], ghcnd_stations[ghcnd_counter][2])
      dist=great_circle(target_latlon, candidate_latlon).miles
      if dist <= distance_limit:
        print ghcnd_stations[ghcnd_counter][0],ghcnd_stations[ghcnd_counter][1],ghcnd_stations[ghcnd_counter][2],ghcnd_stations[ghcnd_counter][3],ghcnd_stations[ghcnd_counter][4],ghcnd_stations[ghcnd_counter][5]
		
  else:
    print "USAGE\n  NAME or\n  LAT LON DIST"
    return None
  return None
  
#################################################
# MODULE: get_metadata
# Get Metadata From Station
# 2 sources
#    - ghcnd-stations.txt
#    - Historical Observing Metadata Repository
#      (HOMR)
#################################################
def get_metadata(station_id):

  # Get Metadata info from station Inventory file
  ghcnd_stations=gp.get_ghcnd_stations()  
  ghcnd_meta = ghcnd_stations[ghcnd_stations[:,0] == station_id]

  ghcnd_name="N/A"
  ghcnd_lat="N/A"
  ghcnd_lon="N/A"
  ghcnd_alt="N/A"

  ghcnd_id=ghcnd_meta[0][0]
  ghcnd_lat=float(ghcnd_meta[0][1])
  ghcnd_lon=float(ghcnd_meta[0][2])
  ghcnd_alt=float(ghcnd_meta[0][3])
  ghcnd_name=ghcnd_meta[0][5]
  ghcnd_name = ghcnd_name.strip()
  ghcnd_name = re.sub(' +',' ',ghcnd_name)
  ghcnd_name = ghcnd_name.replace(" ","_")
      
  # Get Metadata info from HOMR
  homr_link='http://www.ncdc.noaa.gov/homr/services/station/search?qid=GHCND:'+station_id
  
  ghcnd_state="N/A"
  ghcnd_climdiv="N/A"
  ghcnd_county="N/A"
  ghcnd_nwswfo="N/A"
  ghcnd_coopid="N/A"
  ghcnd_wbanid="N/A"

  try:
    homr=r.get(homr_link)
    homr_json=json.loads(homr.text)
  except: 
    pass
  
  # Get State Station is in (HOMR)
  try:
    ghcnd_state=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['climateDivisions'][0]['stateProvince'])
  except:
    pass

  # Get Climate Division Station is in (HOMR)
  try:
    ghcnd_climdiv=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['climateDivisions'][0]['climateDivision'])
  except:
    pass

  # Get County Station is in (HOMR)
  try:
    ghcnd_county=json.dumps(homr_json['stationCollection']['stations'][0]['location']['geoInfo']['counties'][0]['county'])
    ghcnd_county=ghcnd_county.replace(" ","_")
  except:
    pass

  # Get NWS WFO station is in (HOMR)
  try:
    ghcnd_nwswfo=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['nwsWfos'][0]['nwsWfo'])
  except:
    pass
    
  # Get COOP ID if exists (HOMR)
  has_coop=False
  has_wban=False
  try:
    identifiers=homr_json['stationCollection']['stations'][0]['identifiers']
    for counter in xrange(0,10):
      for key, value in homr_json['stationCollection']['stations'][0]['identifiers'][counter].iteritems():
        if key == "idType" and homr_json['stationCollection']['stations'][0]['identifiers'][counter][key] == "COOP":
          has_coop=True
        if key == "idType" and homr_json['stationCollection']['stations'][0]['identifiers'][counter][key] == "WBAN":
          has_wban=True  
          
        if key == "id" and has_coop:
          ghcnd_coopid=homr_json['stationCollection']['stations'][0]['identifiers'][counter][key]
          has_coop=False
        if key == "id" and has_wban:
          ghcnd_wbanid=homr_json['stationCollection']['stations'][0]['identifiers'][counter][key]
          has_wban=False               
  except:
    pass  

  # Write everything out
  print station_id
  print "    Station Name: ",ghcnd_name
  print "    Station Lat: ",ghcnd_lat
  print "    Station Lon: ",ghcnd_lon
  print "    Station Elev: ",ghcnd_alt
  print "    Station State: ",ghcnd_state.strip('""')
  print "    Station Climate Division: ",ghcnd_climdiv.strip('""')
  print "    Station County: ",ghcnd_county.strip('""')
  print "    Station NWS Office: ",ghcnd_nwswfo.strip('""')
  print "    Station COOP ID: ",ghcnd_coopid.strip('""')
  print "    Station WBAN ID: ",ghcnd_wbanid.strip('""')
  return None