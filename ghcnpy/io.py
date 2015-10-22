# Import Modules
import numpy as np
from ftplib import FTP
    
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