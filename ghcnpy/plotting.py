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
import matplotlib.colors as mcolors
from datetime import datetime, date
import matplotlib.colors as colors
import pylab
import gzip
from mpl_toolkits.basemap import Basemap, maskoceans
import ghcnpy as gp

#################################################
# MODULE: plot_temperature
# Plot Temperature Data for a given station
#################################################  
def plot_temperature(station_id,begin_date,end_date):  
  print "\nPLOTTING TEMPERATURE DATA FOR STATION: ",station_id

  # Declare Other Variables
  begin_year=1895
  num_elements=2 # TMAX/TMIN
  tmax=0
  tmin=1
  end_year=datetime.now().year
  num_years=(end_year-begin_year) + 1

  # Get station metadatafile
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
  
  # Grab Data
  gp.get_data_station(station_id)
    
  #################################################
  # Read in GHCN-D Data (Original, QC'd data removed)
  infile = station_id+".dly"
  ghcnd_value = np.zeros((num_years,12,31,num_elements),dtype='f')-(9999.0)

  file_handle = open(infile, 'r')
  contents = file_handle.readlines()
  file_handle.close() 

  for counter in xrange(len(contents)): 

	element = contents[counter][17:21]

	if element == "TMAX" or element == "TMIN":

	  if element == "TMAX":
		element_counter=tmax
	  if element == "TMIN":         
		element_counter=tmin
		   
	  year = int(contents[counter][11:15])
	  year_counter = year-begin_year

	  month = int(contents[counter][15:17])
	  month_counter = month-1

	  char=21
	  for day_counter in xrange(0,31):
		if contents[counter][char:char+5] != "-9999" and contents[counter][char+6:char+7] == " ":
		  ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char+5]) / 10.0
		char = char + 8

  # Mask Missing, convert from C to F
  ghcnd_nonmiss = ma.masked_values(ghcnd_value, -9999.)
  ghcnd_nonmiss=(ghcnd_nonmiss*1.8) + 32 

  # Get Record / Average Values for every day in year
  # For averages, use 1981-2010 
  record_max_ghcnd = np.zeros((12,31),dtype='f')-(9999.0)
  record_min_ghcnd = np.zeros((12,31),dtype='f')-(9999.0)
  average_max_ghcnd = np.zeros((12,31),dtype='f')-(9999.0)
  average_min_ghcnd = np.zeros((12,31),dtype='f')-(9999.0)
  for month_counter in xrange(0,12):
	for day_counter in xrange(0,31):

	  record_max_ghcnd[month_counter,day_counter] = ma.max(ghcnd_nonmiss[:,month_counter,day_counter,tmax])
	  record_min_ghcnd[month_counter,day_counter] = ma.min(ghcnd_nonmiss[:,month_counter,day_counter,tmin])
	  average_max_ghcnd[month_counter,day_counter] = ma.average(ghcnd_nonmiss[(1980-begin_year):(2010-begin_year),month_counter,day_counter,tmax])
	  average_min_ghcnd[month_counter,day_counter] = ma.average(ghcnd_nonmiss[(1980-begin_year):(2010-begin_year),month_counter,day_counter,tmin])

  #################################################
  # Gather Data based Upon Date Requested
  begin_yy = int(begin_date[0:4])
  begin_mm = int(begin_date[4:6])
  begin_dd = int(begin_date[6:8])

  end_yy = int(end_date[0:4])
  end_mm = int(end_date[4:6])
  end_dd = int(end_date[6:8])

  num_days = (date(end_yy, end_mm, end_dd) - date(begin_yy, begin_mm, begin_dd)).days
  num_days=num_days+1

  num_months = ((date(end_yy, end_mm, end_dd).year - date(begin_yy, begin_mm, begin_dd).year)*12 +\
			   date(end_yy, end_mm, end_dd).month - date(begin_yy, begin_mm, begin_dd).month) + 1

  record_max = np.zeros((num_days),dtype='f')-(9999.0)
  record_min = np.zeros((num_days),dtype='f')-(9999.0)
  average_max = np.zeros((num_days),dtype='f')-(9999.0)
  average_min = np.zeros((num_days),dtype='f')-(9999.0)
  raw_max = np.zeros((num_days),dtype='f')-(9999.0)
  raw_min = np.zeros((num_days),dtype='f')-(9999.0)

  month_pos = np.zeros((num_months),dtype='i')-(9999.0)
  month_names = np.empty((num_months),dtype='S7')

  num_days=0
  num_months=0
  for year_counter in xrange(begin_yy,end_yy+1):

	if year_counter == begin_yy:
	  start_month=begin_mm
	  end_month=12
	elif year_counter == end_yy:
	  start_month=1
	  end_month=end_mm
	else:
	  start_month=1
	  end_month=12
	for month_counter in xrange(start_month,end_month+1):
	  month_pos[num_months] = num_days
	  month_names[num_months] = calendar.month_name[month_counter][0:3]+" '"+str(year_counter)[2:4]

	  for day_counter in xrange(begin_dd,end_dd+1):
		try:
		  # Check if date is valid
		  datetime(year=year_counter,month=month_counter,day=day_counter)
		  record_max[num_days] = record_max_ghcnd[month_counter-1,day_counter-1]
		  record_min[num_days] = record_min_ghcnd[month_counter-1,day_counter-1]
		  average_max[num_days] = average_max_ghcnd[month_counter-1,day_counter-1]
		  average_min[num_days] = average_min_ghcnd[month_counter-1,day_counter-1]
		  raw_max[num_days] = ghcnd_nonmiss[year_counter-begin_year,month_counter-1,day_counter-1,tmax]
		  raw_min[num_days] = ghcnd_nonmiss[year_counter-begin_year,month_counter-1,day_counter-1,tmin]
		  num_days=num_days+1
		except:
		  pass
	  num_months=num_months+1
	
  x_axis=range(num_days)  
  
  #################################################
  # PLOT
  fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

  # Add grid lines
  plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

  # Plot Record TMAX/TMIN
  plt.bar(x_axis, record_max - record_min, bottom=record_min, edgecolor='none', color='#c3bba4', width=1, label="Record Max/Min")

  # Plot Average TMAX/TMIN
  plt.bar(x_axis, average_max - average_min, bottom=average_min, edgecolor='none', color='#9a9180', width=1, label="Average Max/Min")

  # Plot Raw TMAX/TMIN
  plt.bar(x_axis, raw_max - raw_min, bottom=raw_min, edgecolor='black', linewidth=0.5, color='#5a3b49', width=1, label="Actual Max/Min")

  # Find New Max/Min Records 
  new_max_records = raw_max[raw_max >= record_max]
  new_min_records = raw_min[raw_min <= record_min]

  # Plot New Max/Min Records
  plt.scatter(np.where(raw_max >= record_max)[0] + 0.5, new_max_records + 1.25, s=15, zorder=10, color='#d62728', alpha=0.75, linewidth=0, label="New Max Record")
  plt.scatter(np.where(raw_min <= record_min)[0] + 0.5, new_min_records - 1.25, s=15, zorder=10, color='#1f77b4', alpha=0.75, linewidth=0, label="New Min Record")

  # Plot Legend
  plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=5, mode="expand", borderaxespad=0., fontsize=12)

  # Plot X/Y Limits
  ymin=int(5 * round(float((min(record_min) - 10))/5))
  ymax=int(5 * round(float((max(record_max) + 10))/5))
  plt.ylim(ymin, ymax)
  plt.xlim(-5, (num_days))

  # Plot Y-Axis Label
  plt.yticks(range(ymin, ymax, 10), [r'{}$^\circ$'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylabel(r'Temperature ($^\circ$F)', fontsize=12)

  # Plot X-Axis Label
  plt.xticks(month_pos, month_names, fontsize=10)

  # Plot 2nd Y Axis Labels
  ax3 = ax1.twinx()
  plt.yticks(range(ymin, ymax, 10), [r'{}$^\circ$'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylim(ymin, ymax)

  # Plot Title/Subtitle
  plt.suptitle(station_id+': '+ghcnd_name, fontsize=20)
  plt.title('LAT= '+str(ghcnd_lat)+' | LON= '+str(ghcnd_lon)+' | ELEV= '+str(int(ghcnd_alt*3.2808399))+'\'', fontsize=15)

  # Save Figure
  plt.savefig(station_id+'_temperature.png', dpi=300)  
  plt.clf()
  return None

#################################################
# MODULE: plot_precipitation
# Plot Accum. Precip Data for a given station
#################################################  
def plot_precipitation(station_id):    
  print "\nPLOTTING PRECIPITATION DATA FOR STATION: ",station_id
  
  # Declare Other Variables
  begin_year=1895
  num_elements=1 # PRCP
  prcp=0
  num_days=366

  end_year=datetime.now().year
  num_years=(end_year-begin_year) + 1
  
  # Get station metadatafile
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
  
  # Grab Data
  gp.get_data_station(station_id)

  #################################################
  # Read in GHCN-D Data (Original, QC'd data removed)
  infile = station_id+".dly"
  ghcnd_value = np.zeros((num_years,12,31,num_elements),dtype='f')

  file_handle = open(infile, 'r')
  contents = file_handle.readlines()
  file_handle.close() 

  valid_end=-9999
  valid_begin=9999
  for counter in xrange(len(contents)): 

	element = contents[counter][17:21]

	if element == "PRCP":
	  element_counter=prcp
	
	  year = int(contents[counter][11:15])
	  year_counter = year-begin_year
	  valid_begin=min(valid_begin,year)
	  valid_end=max(valid_end,year)

	  month = int(contents[counter][15:17])
	  month_counter = month-1

	  char=21
	  for day_counter in xrange(0,31):
		if contents[counter][char:char+5] != "-9999" and contents[counter][char+6:char+7] == " ": # Remove QC
		#if contents[counter][char:char+5] != "-9999":                                              # Do Not Remove QC
		  ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char+5]) / 10.0
		  last_day=day_counter+1
		char = char + 8

  # Get day of year for last day with valid data
  last_day=datetime(year, month, last_day).timetuple().tm_yday

  # Convert from mm to inch
  ghcnd_value=(ghcnd_value*0.0393701)

  # Get Record / Average Values for every day in year
  average_prcp = np.zeros((num_days),dtype='f')-(9999.0)
  day_of_year=0
  day_before=0
  for month_counter in xrange(0,12):
	for day_counter in xrange(0,31):
	  try:
		# Check if leap-year date is valid
		datetime(year=2012,month=month_counter+1,day=day_counter+1)

		average_prcp[day_of_year] = day_before + ma.average(ghcnd_value[(valid_begin-begin_year):(valid_end-begin_year),month_counter,day_counter,prcp])
		day_before=average_prcp[day_of_year]
	  
		day_of_year=day_of_year+1
	  except:
		pass 

  #################################################
  # Create Accumulations
  prcp_accum = np.zeros((num_years,num_days),dtype='f')
  total_accum = np.zeros((num_years),dtype='f')
  for year_counter in xrange(0,num_years):
	day_of_year=0
	day_before=0
	for month_counter in xrange(0,12):
	  for day_counter in xrange(0,31):
		try:
		  # Check if date is valid
		  datetime(year=year_counter+begin_year,month=month_counter+1,day=day_counter+1)
		  prcp_accum[year_counter][day_of_year] = day_before + ghcnd_value[year_counter,month_counter,day_counter,prcp]
		  total_accum[year_counter]=prcp_accum[year_counter][day_of_year]
		  day_before=prcp_accum[year_counter][day_of_year]
		
		  day_of_year=day_of_year+1
		except:
		  pass   
		
  #################################################
  # PLOT

  # Mask Zero Data before plotting
  prcp_accum = ma.masked_values(prcp_accum, 0.)
  total_accum = ma.masked_values(total_accum, 0.)

  #Get Some Stats Needed For Plotting
  x_axis=range(num_days)
  x_axis_end=range(last_day)

  # Current Year
  current_loc = num_years-1
  current_prcp = "%6.2f" % total_accum[current_loc]
  current_year = current_loc + begin_year
  current_data=prcp_accum[current_loc,0:last_day]
  current_last=prcp_accum[current_loc,last_day]

  max_prcp = "%6.2f" % np.max(total_accum)
  max_loc = np.argmax(total_accum)
  max_year = max_loc+begin_year

  min_prcp = "%6.2f" % np.min(total_accum[np.where(total_accum != 0)])
  min_loc = np.nanargmin(total_accum)
  min_year = min_loc+begin_year

  # Average Year
  avg_prcp = "%6.2f" % average_prcp[365]

  # Create Figure
  fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

  # Add grid lines
  plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

  # Plot Accumulated PRCP (Sort by end of year accumulation and plot by range of color)
  order=np.argsort(prcp_accum[:,364])
  color_pos=np.linspace(0.5,1,num_years)
  order_counter=0
  color_counter=0
  for year_counter in xrange(0,num_years):
	pos=order[order_counter]
	if pos != (num_years-1):
	  plt.plot(x_axis, prcp_accum[pos,:], linewidth=0.5, color=colors.rgb2hex(pylab.cm.GnBu(color_pos[color_counter])[0:3]))  
	  color_counter=color_counter+1
	order_counter=order_counter+1

  # Overlay Record Max Prcp Year
  if max_loc==current_loc:
	plt.plot(x_axis_end, prcp_accum[max_loc,0:last_day], color='#084081', linewidth=3, label='Max ('+str(max_year)+': '+str(max_prcp)+'")')  
  else:
	plt.plot(x_axis, prcp_accum[max_loc,:], color='#084081', linewidth=3, label='Max ('+str(max_year)+': '+str(max_prcp)+'")')  
  
  # Overlay Record Min Prcp Year
  if min_loc==current_loc:
	plt.plot(x_axis_end, prcp_accum[min_loc,0:last_day], color='#66ff99', linewidth=3, label='Min ('+str(min_year)+': '+str(min_prcp)+'")')
  else:
	plt.plot(x_axis, prcp_accum[min_loc,:], color='#66ff99', linewidth=3, label='Min ('+str(min_year)+': '+str(min_prcp)+'")')  

  # Overlay Average PRCP
  plt.plot(x_axis, average_prcp[:], color='#e6b800', linewidth=3, markeredgecolor='white', label='Avg ('+str(avg_prcp)+'")') 

  # Overlay Current Prcp Year
  plt.plot(x_axis_end, current_data, color='black', linewidth=3, label='Current ('+str(current_year)+': '+str(current_prcp)+'")')    
  plt.plot(x_axis_end[last_day-1],current_last, marker='o', color='black', markersize=10)

  # Plot Legend
  plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=4, mode="expand", borderaxespad=0., fontsize=12)

  # Plot X/Y Limits
  ymin=0
  ymax=int(5 * round(float((np.max(prcp_accum) + 10))/5))
  plt.ylim(ymin,ymax)
  plt.xlim(-5, num_days) 

  # Plot Y-Axis Label
  plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylabel(r'Accumulated Precip (inches)', fontsize=12)

  # Plot X-Axis Label
  month_pos=[0,31,60,91,121,152,182,213,244,274,305,335]
  month_names=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
  plt.xticks(month_pos, month_names, fontsize=10)

  # Plot 2nd Y Axis Labels
  ax3 = ax1.twinx()
  plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylim(ymin, ymax)

  # Plot Title/Subtitle
  plt.suptitle(station_id+': '+ghcnd_name, fontsize=20)
  plt.title('LAT= '+str(ghcnd_lat)+' | LON= '+str(ghcnd_lon)+' | ELEV= '+str(int(ghcnd_alt*3.2808399))+'\'', fontsize=15)

  #plt.annotate('Source: NCEI | @jjrennie', xy=(0, 0.95), xycoords='axes fraction', fontsize=12,horizontalalignment='left', verticalalignment='top')

  # Save Figure
  plt.savefig(station_id+'_precipitation.png', dpi=300)
  plt.clf()
  return None

#################################################
# MODULE: plot_snowfall
# Plot Accum. Snow Data for a given station
#################################################  
def plot_snowfall(station_id):    
  print "\nPLOTTING SNOWFALL DATA FOR STATION: ",station_id
  
  # Declare Other Variables
  begin_year=1895
  num_elements=1 # SNOW
  snow=0
  num_days=366

  end_year=datetime.now().year
  num_years=(end_year-begin_year) + 1
  
  # Get station metadatafile
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
  
  # Grab Data
  gp.get_data_station(station_id)

  #################################################
  # Read in GHCN-D Data (Original, QC'd data removed)
  infile = station_id+".dly"
  ghcnd_value = np.zeros((num_years,12,31,num_elements),dtype='f')

  file_handle = open(infile, 'r')
  contents = file_handle.readlines()
  file_handle.close() 

  valid_end=-9999
  valid_begin=9999
  for counter in xrange(len(contents)): 

	element = contents[counter][17:21]

	if element == "SNOW":
	  element_counter=snow
	
	  year = int(contents[counter][11:15])
	  year_counter = year-begin_year
	  valid_begin=min(valid_begin,year)
	  valid_end=max(valid_end,year)

	  month = int(contents[counter][15:17])
	  month_counter = month-1

	  char=21
	  for day_counter in xrange(0,31):
		if contents[counter][char:char+5] != "-9999" and contents[counter][char+6:char+7] == " ":
		  ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char+5]) 
		  last_day=day_counter+1
		char = char + 8

  # Get day of year for last day with valid data
  last_day=datetime(year, month, last_day).timetuple().tm_yday
  last_day=last_day+92 # Shift three months
  if last_day >=365:
    last_day=last_day-365

  # Convert from mm to inch
  ghcnd_value=(ghcnd_value*0.0393701)

  # Get Record / Average Values for every day in year
  average_snow = np.zeros((num_days),dtype='f')-(9999.0)
  day_of_year=0
  day_before=0
  for month_counter in [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
	for day_counter in xrange(0,31):
	  try:
		# Check if leap-year date is valid
		datetime(year=2012,month=month_counter+1,day=day_counter+1)

		average_snow[day_of_year] = day_before + ma.average(ghcnd_value[(valid_begin-begin_year):(valid_end-begin_year),month_counter,day_counter,snow])
		day_before=average_snow[day_of_year]
	  
		day_of_year=day_of_year+1
	  except:
		pass 

  #################################################
  # Create Accumulations 
  new_year_counter=0
  snow_accum = np.zeros((num_years+1,num_days),dtype='f')
  total_accum = np.zeros((num_years+1),dtype='f')
  for year_counter in xrange(0,num_years):
	for month_counter in xrange(0,12):
	  if month_counter==9: # Month Begins in Oct
		new_year_counter=year_counter+1
		day_of_year=0
		day_before=0
	  for day_counter in xrange(0,31):
		try:
		  # Check if date is valid
		  datetime(year=year_counter+begin_year,month=month_counter+1,day=day_counter+1)
		  snow_accum[new_year_counter][day_of_year] = day_before + ghcnd_value[year_counter,month_counter,day_counter,snow]
		  total_accum[new_year_counter]=snow_accum[new_year_counter][day_of_year]
		  day_before=snow_accum[new_year_counter][day_of_year]
		  day_of_year=day_of_year+1
		except:
		  pass
	  if month_counter+1==12 and snow_accum[year_counter][365]==0:
		snow_accum[year_counter][365]=snow_accum[year_counter][364]
	  
  #################################################
  # PLOT
  # Mask Zero Data before plotting
  #snow_accum = ma.masked_values(snow_accum, 0.)
  total_accum = ma.masked_values(total_accum, 0.)

  #Get Some Stats Needed For Plotting
  x_axis=range(num_days)
  x_axis_end=range(last_day)

  current_loc = num_years-1
  current_snow = "%6.2f" % total_accum[current_loc]
  current_year = current_loc + begin_year
  current_data=snow_accum[current_loc,0:last_day]
  current_last=snow_accum[current_loc,last_day]

  max_snow = "%6.2f" % np.max(total_accum)
  max_loc = np.argmax(total_accum)
  max_year = max_loc+begin_year

  min_snow = "%6.2f" % np.min(total_accum[np.where(total_accum != 0)])
  min_loc = np.nanargmin(total_accum)
  min_year = min_loc+begin_year

  avg_snow = "%6.2f" % average_snow[365]

  # Create Figure
  fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

  # Add grid lines
  plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

  # Plot Accumulated SNOW (Sort by end of year accumulation and plot by range of color)
  order=np.argsort(snow_accum[:,364])
  color_pos=np.linspace(0.5,1,num_years)
  order_counter=0
  color_counter=0
  for year_counter in xrange(0,num_years):
	pos=order[order_counter]
	if pos != (num_years-1):
	  plt.plot(x_axis, snow_accum[pos,:], linewidth=0.5, color=colors.rgb2hex(pylab.cm.GnBu(color_pos[color_counter])[0:3]))  
	  color_counter=color_counter+1
	order_counter=order_counter+1

  # Overlay Record Max Snow Year
  if max_loc==current_loc:
	plt.plot(x_axis_end, snow_accum[max_loc,0:last_day], color='#084081', linewidth=3, label='Max ('+str(max_year-1)+'-'+str(max_year)+': '+str(max_snow)+'")')  
  else:
	plt.plot(x_axis, snow_accum[max_loc,:], color='#084081', linewidth=3, label='Max ('+str(max_year-1)+'-'+str(max_year)+': '+str(max_snow)+'")')  
  
  # Overlay Record Min Snow Year
  if min_loc==current_loc:
	plt.plot(x_axis_end, snow_accum[min_loc,0:last_day], color='#66ff99', linewidth=3, label='Min ('+str(min_year-1)+'-'+str(min_year)+': '+str(min_snow)+'")')
  else:
	plt.plot(x_axis, snow_accum[min_loc,:], color='#66ff99', linewidth=3, label='Min ('+str(min_year-1)+'-'+str(min_year)+': '+str(min_snow)+'")')  

  # Overlay Average SNOW
  plt.plot(x_axis, average_snow[:], color='#e6b800', linewidth=3, markeredgecolor='white', label='Avg ('+str(avg_snow)+'")') 

  # Overlay Current Snow Year
  plt.plot(x_axis_end, current_data, color='black', linewidth=3, label='Current ('+str(current_year-1)+'-'+str(current_year)+': '+str(current_snow)+'")')    
  plt.plot(x_axis_end[last_day-1],current_last, marker='o', color='black', markersize=10)

  # Plot Legend
  plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=4, mode="expand", borderaxespad=0., fontsize=12)

  # Plot X/Y Limits
  ymin=0
  ymax=int(5 * round(float((np.max(snow_accum) + 10))/5))
  plt.ylim(ymin,ymax)
  plt.xlim(-5, num_days) 

  # Plot Y-Axis Label
  plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylabel(r'Accumulated Snowfall (inches)', fontsize=12)

  # Plot X-Axis Label
  month_pos=[0,31,60,91,121,152,182,213,244,274,305,335]
  month_names=["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]
  plt.xticks(month_pos, month_names, fontsize=10)

  # Plot 2nd Y Axis Labels
  ax3 = ax1.twinx()
  plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
  plt.ylim(ymin, ymax)

  # Plot Title/Subtitle
  plt.suptitle(station_id+': '+ghcnd_name, fontsize=20)
  plt.title('LAT= '+str(ghcnd_lat)+' | LON= '+str(ghcnd_lon)+' | ELEV= '+str(int(ghcnd_alt*3.2808399))+'\'', fontsize=15)

  # Save Figure
  plt.savefig(station_id+'_snowfall.png', dpi=300)    
  plt.clf()
  return None
  
#################################################
# MODULE: plot_spatial
# Plot Data Spatially for a given date
# Uses GHCN-D Six Major Elements
#     TMAX/TMIN/TAVG/PRCP/SNOW/SNWD
#################################################  
def plot_spatial(year,month,day,element,lower_lon=-125,upper_lon=-65,lower_lat=25,upper_lat=50,dpi=200,proj='merc'):    
  print "\nPLOT SPATIAL"
  
  if month < 10:
    month="0"+str(month)

  if day < 10:
    day="0"+str(day)
    
  print "year: ",year
  print "month: ",month
  print "day: ",day
  print "element: ",element
  
  plot_date=str(year)+str(month)+str(day)
    
  if element != "TMAX" and element != "TMIN" and element != "TAVG" and element != "PRCP" and element != "SNOW" and element != "SNWD":
	print "Only Elements Available: TMAX/TMIN/TAVG/PRCP/SNOW/SNWD"
	return None

  # Set info based on Element
  if element == "TMAX" or element == "TMIN" or element == "TAVG":
	divisor=10.
	unit='$^\circ$F'

	# Initialize Colormap Values
	cbar_hex = ['#072F6B', '#08529C', '#2171B5', '#176fc1', '#0b8ed8', '#04a1e6', '#19b5f1', '#33bccf', '#66ccce', 
				'#99dbb8', '#c0e588', '#cce64b', '#f3f01d', '#fede27', '#fcc707', '#f89d0e', '#f57215', '#f1471c', 
				'#db1e26', '#a4262c', '#A60F14' ]
	cbar_vals = np.array([0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100], dtype='f')

	# Set Up Colormap based element-based values
	cmap=mcolors.ListedColormap(cbar_hex, N=len(cbar_vals))
	norm = mcolors.BoundaryNorm(cbar_vals, cmap.N)
	minimum = min(cbar_vals); maximum = max(cbar_vals) # set range.
	cmap.set_under("#071E46")
	cmap.set_over("#5F0000")
	extend="both"

  if element == "PRCP":
	divisor=10.
	unit='inches'  

	# Initialize Colormap Values
	cbar_hex = [ '#33ffff', '#0099ff', '#0033cc', '#33ff00', '#33cc00','#336600', '#ffff33', '#cc9900', '#ff9900', 
				 '#ff0000','#cc0000', '#990000', '#ff00ff', '#9900ff', '#9900ff' ]
	cbar_vals = np.array([0.01,0.10,0.25,0.50,0.75,1.0,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0], dtype='f')

	# Set Up Colormap based element-based values
	cmap=mcolors.ListedColormap(cbar_hex, N=len(cbar_vals))
	norm = mcolors.BoundaryNorm(cbar_vals, cmap.N)
	minimum = min(cbar_vals); maximum = max(cbar_vals) # set range.
	cmap.set_over("#ffffff")
	extend="max"

  if element == "SNOW" or element == "SNWD":
	divisor=1.
	unit='inches'

	# Initialize Colormap Values
	cbar_hex = [ '#EDFAC2', '#CDFFCD', '#99ff99', '#53bd9f', '#32a696', '#3296b4', '#0570b0', '#05508c', '#0a1f96', 
				 '#6a2c5a', '#6a2c5a' ]
	cbar_vals = np.array([0.01,1.,2.,3.,4.,5.,10.,15.,20.,30.,40.], dtype='f')

	# Set Up Colormap based element-based values
	cmap=mcolors.ListedColormap(cbar_hex, N=len(cbar_vals))
	norm = mcolors.BoundaryNorm(cbar_vals, cmap.N)
	minimum = min(cbar_vals); maximum = max(cbar_vals) # set range.
	cmap.set_over("#2c0246")
	extend="max"

  #################################################
  # Read in GHCND-D Inventory File to get
  # stations that have element requested
  print "GETTING STATIONS THAT MATCH ELEMENT: ",element

  ghcnd_inventory=gp.get_ghcnd_inventory()  
  ghcnd_stations = ghcnd_inventory[ghcnd_inventory[:,3] == element]
  num_stns=ghcnd_stations.shape[0]

  ghcnd_values = np.zeros((num_stns),dtype='f')-(9999.0)
  ghcnd_lats = np.zeros((num_stns),dtype='f')-(9999.0)
  ghcnd_lons = np.zeros((num_stns),dtype='f')-(9999.0)

  #################################################
  # Read in GHCN-D data
  print "READING IN DATA"
  gp.get_data_year(str(year))
  
  infile = str(year)+".csv.gz"
  
  file_handle = gzip.open(infile, 'rb')
  ghcnd_contents = file_handle.readlines()
  file_handle.close()

  valid_stns=0
  for counter in xrange(len(ghcnd_contents)): 

	ghcnd_line = ghcnd_contents[counter].split(',')
	if ghcnd_line[1] == plot_date and ghcnd_line[2] == element:
	  # Get Data Value
	  ghcnd_values[valid_stns] = (float(ghcnd_line[3])/divisor)

	  # Get Lat/Lon
	  ghcnd_meta = ghcnd_stations[ghcnd_stations[:,0] == ghcnd_line[0]]
	  ghcnd_lats[valid_stns]=float(ghcnd_meta[0][1])
	  ghcnd_lons[valid_stns]=float(ghcnd_meta[0][2])
	  valid_stns=valid_stns+1

  # Sort from lowest to highest (so higher values are plotted over lower values)
  sorted=np.ma.argsort(ghcnd_values)
  ghcnd_values=ghcnd_values[sorted]
  ghcnd_lats=ghcnd_lats[sorted]
  ghcnd_lons=ghcnd_lons[sorted]

  # Convert to Imperial Units and mask data where needed
  if element == "TMAX" or element == "TMIN" or element == "TAVG":
	ghcnd_values = (ghcnd_values * 1.8) + 32. # C to F
  else:
	ghcnd_values = (ghcnd_values * 0.03937) # mm to inch
	ghcnd_values = ma.masked_where(ghcnd_values < 0.01, ghcnd_values)

  # Don't Plot Missing Data
  valid=np.where(np.logical_and(ghcnd_lats!=-9999,ghcnd_lons!=-9999))

  #################
  # PLOT
  print "PLOTTING (POINT DATA)"
  plt.figure(num=1, figsize=(10, 6), dpi=dpi, facecolor='w', edgecolor='k') 

  # Create Mercator Basemaps
  map_points = Basemap(projection=proj,llcrnrlon=lower_lon,llcrnrlat=lower_lat,
			   urcrnrlon=upper_lon,urcrnrlat=upper_lat, resolution='h')          

  # draw coastlines, country boundaries, fill continents.
  map_points.drawcoastlines(linewidth=0.25)
  map_points.drawcountries(linewidth=0.25)
  map_points.drawstates(linewidth=0.25)

  # Plot Data
  x, y = map_points(ghcnd_lons[valid],ghcnd_lats[valid])
  map_points.scatter(x,y,c=ghcnd_values[valid],s=10,cmap=cmap,vmin=minimum,vmax=maximum,linewidths=0.1)

  # Adds the colormap legend
  cmleg = np.zeros((1,len(cbar_vals)),dtype='f')
  for i in xrange(0,(len(cbar_vals))):
	  cmleg[0,i] = float(cbar_vals[i])

  # Add Colorbar 
  cmap_legend=plt.imshow(cmleg, cmap=cmap, norm=norm)
  cbar = map_points.colorbar(location='bottom',pad="5%",ticks=cbar_vals,extend=extend)
  cbar.ax.tick_params(labelsize=10) 
  cbar.set_label(unit)

  # add title
  plt.title(element+' data for '+str(year)+' '+str(month)+' '+str(day))

  # Save to file
  plt.savefig('POINT_'+str(element)+'_'+str(plot_date)+'.png', format='png', dpi=dpi)
  plt.clf()
  return None

#################################################
# MODULE: plot_spatial_derived
# Special Version of plot_spatial where
# Derived elements are plotted 
#     HDD/CDD/GDD
#################################################  
def plot_spatial_derived(year,element,lower_lon=-125,upper_lon=-65,lower_lat=25,upper_lat=50,dpi=200,proj='merc'):    
  print "\nPLOT SPATIAL DERIVED"

  print "year: ",year
  print "element: ",element

  days_in_year=(datetime(year, 12, 31)-datetime(year, 1, 1)).days+1

  if element != "GDD" and element != "HDD" and element != "CDD":
    print "Only Derived Elements Available: GDD/HDD/CDD"
    return None
    
  # Set info based on Element
  if element == "GDD" or element == "HDD" or element == "CDD":
	divisor=10.

	if element == "HDD":
	  # Initialize Colormap Values (Reds to Blues)
	  cbar_hex = ['#A60F14', '#a4262c', '#db1e26', '#f1471c', '#f57215', '#f89d0e', '#fcc707', '#fede27', '#f3f01d',
				 '#cce64b', '#c0e588', '#99dbb8', '#66ccce', '#33bccf', '#19b5f1', '#04a1e6', '#0b8ed8', '#176fc1', 
				 '#2171B5', '#08529C', '#072F6B' ]
	if element == "CDD" or element == "GDD":
	  # Initialize Colormap Values (Blues to Reds)
	  cbar_hex = ['#072F6B', '#08529C', '#2171B5', '#176fc1', '#0b8ed8', '#04a1e6', '#19b5f1', '#33bccf', '#66ccce', 
				  '#99dbb8', '#c0e588', '#cce64b', '#f3f01d', '#fede27', '#fcc707', '#f89d0e', '#f57215', '#f1471c', 
				  '#db1e26', '#a4262c', '#A60F14' ] 
	cbar_vals = np.array([0,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000], dtype='f')

	# Set Up Colormap based element-based values
	cmap=mcolors.ListedColormap(cbar_hex, N=len(cbar_vals))
	norm = mcolors.BoundaryNorm(cbar_vals, cmap.N)
	minimum = min(cbar_vals); maximum = max(cbar_vals) # set range.
	cmap.set_under("#ffffff")
	cmap.set_over("#5F0000")
	extend="max"

  #################################################
  # Read in GHCND-D Inventory File to get
  # stations that have element requested
  print "GETTING STATIONS"

  ghcnd_stations=gp.get_ghcnd_inventory()  
  num_stns=ghcnd_stations.shape[0]

  ghcnd_valid_id = np.empty(num_stns,dtype='S11')
  ghcnd_tmax = np.zeros((num_stns,days_in_year),dtype='f')-(9999.0)
  ghcnd_tmin = np.zeros((num_stns,days_in_year),dtype='f')-(9999.0)
  ghcnd_lats = np.zeros((num_stns,days_in_year),dtype='f')-(9999.0)
  ghcnd_lons = np.zeros((num_stns,days_in_year),dtype='f')-(9999.0)

  #################################################
  # Read in GHCN-D data
  print "READING IN DATA"
  gp.get_data_year(str(year))

  infile = str(year)+".csv.gz"

  file_handle = gzip.open(infile, 'rb')
  ghcnd_contents = file_handle.readlines()
  file_handle.close()

  print "SORTING"
  ghcnd_contents=np.sort(ghcnd_contents)

  print "GOING THROUGH DATA"
  # Go through GHCN-D Data  
  station_counter=-1
  old_id = "XXXXXXXXXXX"
  num_valid=0
  for counter in xrange(len(ghcnd_contents)): 
	ghcnd_line = ghcnd_contents[counter].split(',')

	if ghcnd_line[2] == "TMAX" or ghcnd_line[2] == "TMIN":
	  if old_id != ghcnd_line[0]:
		station_counter = station_counter+1
		num_valid=num_valid+1
		ghcnd_valid_id[station_counter] = ghcnd_line[0]
		#print station_counter,ghcnd_valid_id[station_counter]

	  day_in_year=datetime(int(ghcnd_line[1][0:4]),int(ghcnd_line[1][4:6]),int(ghcnd_line[1][6:8])).timetuple().tm_yday-1

	  # Get TMAX/TMIN and its associated lats/lons
	  if ghcnd_line[2] == "TMAX" and ghcnd_line[3] != "-9999" and ghcnd_line[5].strip()=='':
		ghcnd_tmax[station_counter,day_in_year] = (float(ghcnd_line[3])/divisor)
	  if ghcnd_line[2] == "TMIN" and ghcnd_line[3] != "-9999" and ghcnd_line[5].strip()=='':
		ghcnd_tmin[station_counter,day_in_year] = (float(ghcnd_line[3])/divisor)
	  old_id=ghcnd_line[0]


  print "CREATING ACCUMULATIONS"

  ghcnd_derived_lats = np.zeros((num_valid),dtype='f')-(9999.0)
  ghcnd_derived_lons = np.zeros((num_valid),dtype='f')-(9999.0)
  ghcnd_derived_values = np.zeros((num_valid),dtype='f')-(9999.0)

  for station_counter in xrange(0,num_valid):
	ghcnd_meta = ghcnd_stations[ghcnd_stations[:,0] == ghcnd_valid_id[station_counter]]
  
	ghcnd_derived_lats[station_counter]=float(ghcnd_meta[0][1])
	ghcnd_derived_lons[station_counter]=float(ghcnd_meta[0][2])

	ghcnd_value = np.zeros((days_in_year),dtype='f')-(9999.0)  
	non_missing=np.where(np.logical_and(ghcnd_tmax[station_counter] != -9999, ghcnd_tmin[station_counter] != -9999))
	ghcnd_value[non_missing] = (ghcnd_tmax[station_counter,non_missing] + ghcnd_tmin[station_counter,non_missing]) / 2.  

	if element == "GDD":
	  base=10.000
	  ghcnd_value[non_missing] = ghcnd_value[non_missing] - base
	if element == "HDD":
	  base=18.333
	  ghcnd_value[non_missing] = base - ghcnd_value[non_missing]
	if element == "CDD":
	  base=18.333
	  ghcnd_value[non_missing] = ghcnd_value[non_missing] - base

	non_zero=np.where(ghcnd_value > 0)
	ghcnd_derived_values[station_counter]=np.sum(ghcnd_value[non_zero])

  # Sort from lowest to highest (so higher values are plotted over lower values)
  sorted=np.ma.argsort(ghcnd_derived_values)
  ghcnd_derived_values=ghcnd_derived_values[sorted]
  ghcnd_derived_lats=ghcnd_derived_lats[sorted]
  ghcnd_derived_lons=ghcnd_derived_lons[sorted]

  #################
  # PLOT
  print "PLOTTING (POINT DATA)"
  plt.figure(num=1, figsize=(10, 6), dpi=dpi, facecolor='w', edgecolor='k') 

  # Create Mercator Basemaps
  map_points = Basemap(projection=proj,llcrnrlon=lower_lon,llcrnrlat=lower_lat,
			   urcrnrlon=upper_lon,urcrnrlat=upper_lat, resolution='h')          

  # draw coastlines, country boundaries, fill continents.
  map_points.drawcoastlines(linewidth=0.25)
  map_points.drawcountries(linewidth=0.25)
  map_points.drawstates(linewidth=0.25)

  # Plot Data
  x, y = map_points(ghcnd_derived_lons,ghcnd_derived_lats)
  map_points.scatter(x,y,c=ghcnd_derived_values,s=10,cmap=cmap,vmin=minimum,vmax=maximum,linewidths=.1)
  
  # Adds the colormap legend
  cmleg = np.zeros((1,len(cbar_vals)),dtype='f')
  for i in xrange(0,(len(cbar_vals))):
	  cmleg[0,i] = float(cbar_vals[i])
 
  # Add Colorbar 
  cmap_legend=plt.imshow(cmleg, cmap=cmap, norm=norm)
  cbar = map_points.colorbar(location='bottom',pad="5%",ticks=cbar_vals,extend=extend)
  cbar.ax.tick_params(labelsize=10) 
  cbar.set_label('Degree Days ('+str(base)+' $^\circ$C)')

  # add title
  plt.title(element+' data for '+str(year))

  # Save to file
  plt.savefig('POINT_'+element+'_'+str(year)+'.png', format='png', dpi=dpi)
  plt.clf()
  return None

#################################################
# MODULE: plot_spatial_freeze
# Special Version of plot_spatial where
# First/Last freeze dates are plotted 
# for a given year
#################################################  
def plot_spatial_freeze(year,element,lower_lon=-125,upper_lon=-65,lower_lat=25,upper_lat=50,dpi=200,proj='merc'):    
  print "\nPLOT SPATIAL FREEZE"

  print "year: ",year
  print "element: ",element

  days_in_year=(datetime(year, 12, 31)-datetime(year, 1, 1)).days+1

  divisor=10.

  if element != "LAST" and element != "FIRST":
	print "Only Derived Elements Available: LAST/FIRST"
	return None

  if element == "LAST":
	# Initialize Colormap Values 
	cbar_hex = ['#072F6B', '#08529C', '#2171B5', '#176fc1', '#0b8ed8', '#04a1e6', '#19b5f1', '#33bccf', '#66ccce', 
	'#99dbb8', '#c0e588', '#cce64b' ] 
	cbar_vals = np.array([1,69,79,89,99,109,119,129,139,149,159,169], dtype='f')
  
  if element == "FIRST":
	# Initialize Colormap Values 
	cbar_hex = ['#993399', '#CC0099', '#FF33CC', '#333399', '#3366FF', '#33CCFF', '#006600', '#339933', '#00CC00', 
	'#CC9900', '#FF9900', '#FFCC00' ] 
	cbar_vals = np.array([222,232,242,252,262,272,282,292,302,312,322,332], dtype='f')

  # Set Up Colormap based element-based values
  cmap=mcolors.ListedColormap(cbar_hex, N=len(cbar_vals))
  norm = mcolors.BoundaryNorm(cbar_vals, cmap.N)
  minimum = min(cbar_vals); maximum = max(cbar_vals) # set range.
  cmap.set_under("#ffffff")
  cmap.set_over("#ffffff")
  extend="both"

  #################################################
  # Read in GHCND-D Inventory File to get
  # stations that have element requested
  print "GETTING STATIONS"

  ghcnd_stations=gp.get_ghcnd_inventory()  
  num_stns=ghcnd_stations.shape[0]

  ghcnd_valid_id = np.empty(num_stns,dtype='S11')
  ghcnd_freeze_day = np.zeros((num_stns),dtype='f')

  ghcnd_values = np.zeros((num_stns),dtype='f')-(9999.0)
  ghcnd_lats = np.zeros((num_stns),dtype='f')-(9999.0)
  ghcnd_lons = np.zeros((num_stns),dtype='f')-(9999.0)

  #################################################
  # Read in GHCN-D data
  print "READING IN DATA"
  gp.get_data_year(str(year))

  infile = str(year)+".csv.gz"

  file_handle = gzip.open(infile, 'rb')
  ghcnd_contents = file_handle.readlines()
  file_handle.close()

  print "SORTING"
  ghcnd_contents=np.sort(ghcnd_contents)

  print "GOING THROUGH DATA"
  # Go through GHCN-D Data  
  station_counter=-1
  old_id = "XXXXXXXXXXX"
  num_valid=0
  for counter in xrange(len(ghcnd_contents)): 
	ghcnd_line = ghcnd_contents[counter].split(',')

	if ghcnd_line[2] == "TMIN":
	  if old_id != ghcnd_line[0]:
		station_counter = station_counter+1
		num_valid=num_valid+1
		ghcnd_valid_id[station_counter] = ghcnd_line[0]

	  day_in_year=datetime(int(ghcnd_line[1][0:4]),int(ghcnd_line[1][4:6]),int(ghcnd_line[1][6:8])).timetuple().tm_yday

	  if ghcnd_line[3] != "-9999" and ghcnd_line[5].strip()=='':
		tmin_value = (float(ghcnd_line[3])/divisor)
	  
		if element == "LAST":
		  if tmin_value <=0 and day_in_year <= 169:
			ghcnd_freeze_day[station_counter]=day_in_year
		
		if element == "FIRST":
		  if tmin_value <=0 and day_in_year >= 222 and ghcnd_freeze_day[station_counter] == 0:
			ghcnd_freeze_day[station_counter]=day_in_year      
		  
	  old_id=ghcnd_line[0]

  ghcnd_derived_lats = np.zeros((num_valid),dtype='f')-(9999.0)
  ghcnd_derived_lons = np.zeros((num_valid),dtype='f')-(9999.0)
  ghcnd_derived_values = np.zeros((num_valid),dtype='f')-(9999.0)

  for station_counter in xrange(0,num_valid):
	ghcnd_meta = ghcnd_stations[ghcnd_stations[:,0] == ghcnd_valid_id[station_counter]]
  
	ghcnd_derived_lats[station_counter]=float(ghcnd_meta[0][1])
	ghcnd_derived_lons[station_counter]=float(ghcnd_meta[0][2])
	ghcnd_derived_values[station_counter]=ghcnd_freeze_day[station_counter]
  
  # Sort from lowest to highest (so higher values are plotted over lower values)
  sorted=np.ma.argsort(ghcnd_derived_values)
  ghcnd_derived_values=ghcnd_derived_values[sorted]
  ghcnd_derived_lats=ghcnd_derived_lats[sorted]
  ghcnd_derived_lons=ghcnd_derived_lons[sorted]

  #################
  # PLOT
  print "PLOTTING (POINT DATA)"
  plt.figure(num=1, figsize=(10, 6), dpi=dpi, facecolor='w', edgecolor='k') 

  # Create Mercator Basemaps
  map_points = Basemap(projection=proj,llcrnrlon=lower_lon,llcrnrlat=lower_lat,
			   urcrnrlon=upper_lon,urcrnrlat=upper_lat, resolution='h')          

  # draw coastlines, country boundaries, fill continents.
  map_points.drawcoastlines(linewidth=0.25)
  map_points.drawcountries(linewidth=0.25)
  map_points.drawstates(linewidth=0.25)

  # Plot Data
  x, y = map_points(ghcnd_derived_lons,ghcnd_derived_lats)
  map_points.scatter(x,y,c=ghcnd_derived_values,s=10,cmap=cmap,vmin=minimum,vmax=maximum,linewidths=.1)
  
  # Adds the colormap legend
  cmleg = np.zeros((1,len(cbar_vals)),dtype='f')
  for i in xrange(0,(len(cbar_vals))):
	  cmleg[0,i] = float(cbar_vals[i])
 
  # Add Colorbar 
  cmap_legend=plt.imshow(cmleg, cmap=cmap, norm=norm)
  cbar = map_points.colorbar(location='bottom',pad="5%",ticks=cbar_vals,extend=extend)
  cbar.ax.tick_params(labelsize=10) 
  cbar.set_label('Day of Year')

  # Set Labels Based on Element
  if element == "LAST":
	cbar.ax.set_xticklabels(['Jan-1', 'Mar-10', 'Mar-20', 'Mar-30', 'Apr-10', 'Apr-20', 'Apr-30', 'May-10', 'May-20', 'May-30', 'Jun-10', 'Jun-20'], rotation=30)

	# add title
	plt.title('Last Freeze date for '+str(year))

	# Save to file
	plt.savefig('POINT_LAST-FRZ_'+str(year)+'.png', format='png', dpi=dpi)

  if element == "FIRST":
	cbar.ax.set_xticklabels(['Aug-10', 'Aug-20', 'Aug-31', 'Sep-10', 'Sep-20', 'Sep-30', 'Oct-10', 'Oct-20', 'Oct-31', 'Nov-10', 'Nov-20', 'Nov-30'], rotation=30)

	# add title
	plt.title('First Freeze date for '+str(year))

	# Save to file
	plt.savefig('POINT_FIRST-FRZ_'+str(year)+'.png', format='png', dpi=dpi)

  plt.clf()
  return None