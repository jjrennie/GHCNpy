from ftplib import FTP

def intro():
  print "GHCNpy"
  print "Package to pull, analyze and visualize stations from GHCN-Daily"
  return 
    
def get_data_station(station):
  print "\nget data"
  print "station = "+station

  ftp = FTP('ftp.ncdc.noaa.gov')     # connect to host, default port
  ftp.login()                     # user anonymous, passwd anonymous@
  ftp.cwd('pub/data/ghcn/daily/all')               # change into "debian" directory
  ftp.retrbinary('RETR '+station+'.dly', open(station+'.dly', 'wb').write)
  ftp.quit()

  outfile=station+".dly"
  return outfile
  
def get_data_year(year):
  print "\nget data"
  print "year = "+year

  ftp = FTP('ftp.ncdc.noaa.gov')     # connect to host, default port
  ftp.login()                     # user anonymous, passwd anonymous@
  ftp.cwd('pub/data/ghcn/daily/by_year')               # change into "debian" directory
  ftp.retrbinary('RETR '+year+'.csv.gz', open(year+'.csv.gz', 'wb').write)
  ftp.quit()

  outfile=year+".csv.gz"
  return outfile