from ftplib import FTP
import numpy as np

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
  print ghcnd_stations

  return ghcnd_stations
  
# Find Station ID based on Name
def find_station_id(station_name):
  print "\nFind ID"
  print "name = "+station_name
  
  # Get station metadatafile
  ghcnd_stations=get_ghcnd_stations()  
  print ghcnd_stations[:,5]
  ghcnd_meta = ghcnd_stations[ghcnd_stations[:,5].strip() == station_name]

  return ghcnd_meta
  
# Get Metadata of Station (Add Later)
#def get_metadata(station):
#
#  return None
  
  

