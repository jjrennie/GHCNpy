import ghcnpy

# Provide introduction
ghcnpy.intro()

# Print Latest Version
ghcnpy.get_ghcnd_version()

# Testing Search Capabilities
print("\nTESTING SEARCH CAPABILITIES")
ghcnpy.find_station("Asheville")

# Testing Search Capabilities
print("\nTESTING PULL CAPABILITIES")
outfile=ghcnpy.get_data_station("USW00003812")
print(outfile," has been downloaded")
