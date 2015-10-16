import ghcnpy

ghcnpy.intro()

outfile=ghcnpy.get_data_station("USW00003812")
print outfile

outfile2=ghcnpy.get_data_year("2015")
print outfile2