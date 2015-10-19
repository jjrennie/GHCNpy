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
mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, date

# Introduction to the Program
def intro():
  print "GHCNpy"
  print "Package to pull, analyze and visualize stations from GHCN-Daily"
  return 
    
# Fetch Individual station (.dly ASCII format)
def get_data_station(station):
  print "\nget data"
  print "station = "+station

  ftp = FTP('ftp.ncdc.noaa.gov')    
  ftp.login()                    
  ftp.cwd('pub/data/ghcn/daily/all')       
  ftp.retrbinary('RETR '+station+'.dly', open(station+'.dly', 'wb').write)
  ftp.quit()

  outfile=station+".dly"
  return outfile
  
#  Fetch 1 Year of Data (.csv ASCII format)
def get_data_year(year):
  print "\nget data"
  print "year = "+year

  ftp = FTP('ftp.ncdc.noaa.gov')     
  ftp.login()                   
  ftp.cwd('pub/data/ghcn/daily/by_year')      
  ftp.retrbinary('RETR '+year+'.csv.gz', open(year+'.csv.gz', 'wb').write)
  ftp.quit()

  outfile=year+".csv.gz"
  return outfile

# Get ghcnd-stations.txt file
def get_ghcnd_stations():
  print "\nget ghcnd stations"

  ftp = FTP('ftp.ncdc.noaa.gov')  
  ftp.login()                    
  ftp.cwd('pub/data/ghcn/daily')            
  ftp.retrbinary('RETR ghcnd-stations.txt', open('ghcnd-stations.txt', 'wb').write)
  ftp.quit()
  
  #################################################
  # Read in GHCND-D Stations File  
  ghcnd_stnfile='ghcnd-stations.txt'
  ghcnd_stations= np.genfromtxt(ghcnd_stnfile,delimiter=(11,9,10,7,4,30),dtype=str)

  return ghcnd_stations
  
# Find Station ID based on Name
def find_station(station_name):
  print "\nFind ID"
  print "name = "+station_name
  
  # Get station metadatafile
  ghcnd_stations=get_ghcnd_stations()  

  stns=filter(lambda x: re.search(station_name,x), ghcnd_stations[:,5])
  if(len(stns)==0):
    print "NO STATIONS FOUND"
  else:
    print "GHCND ID          LAT        LON    ELEV  ST       STATION NAME"
    print "###############################################################"
  for station_counter in xrange(len(stns)): 
    ghcnd_meta = ghcnd_stations[ghcnd_stations[:,5]== stns[station_counter]]
    print ghcnd_meta[0][0],ghcnd_meta[0][1],ghcnd_meta[0][2],ghcnd_meta[0][3],ghcnd_meta[0][4],ghcnd_meta[0][5]
  return None
  
# Get Metadata of Station 
def get_metadata(station_id):
  
  # Get Metadata info from HOMR
  homr_link='http://www.ncdc.noaa.gov/homr/services/station/search?qid=GHCND:'+station_id

  try:
    homr=r.get(homr_link)
    homr_json=json.loads(homr.text)
  except: 
    pass
  
  print homr_json
  
  # Get State Station is in (HOMR)
  try:
    state=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['climateDivisions'][0]['stateProvince'])
  except:
    pass

  # Get Climate Division Station is in (HOMR)
  try:
    climdiv=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['climateDivisions'][0]['climateDivision'])
  except:
    pass

  # Get County Station is in (HOMR)
  try:
    county=json.dumps(homr_json['stationCollection']['stations'][0]['location']['geoInfo']['counties'][0]['county'])
    county=county.replace(" ","_")
  except:
    pass

  # Get NWS WFO station is in (HOMR)
  try:
    nwswfo=json.dumps(homr_json['stationCollection']['stations'][0]['location']['nwsInfo']['nwsWfos'][0]['nwsWfo'])
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
          coopid=homr_json['stationCollection']['stations'][0]['identifiers'][counter][key]
          has_coop=False
        if key == "id" and has_wban:
          wbanid=homr_json['stationCollection']['stations'][0]['identifiers'][counter][key]
          has_wban=False               
  except:
    pass  

  # Write everything out to main file (1 file for each station)
  print station_id,state.strip('""'),climdiv.strip('""'),county.strip('""').upper(),nwswfo.strip('""'),coopid,wbanid
  return 