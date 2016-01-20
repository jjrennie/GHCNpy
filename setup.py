from setuptools import setup, find_packages

setup(
    name='GHCNpy',
    version='1.0',
    author='Jared Rennie, Samuel Lillo',
    author_email='jared@cicsnc.org, splillo@ou.edu',
    packages=find_packages(),
    url='https://github.com/jjrennie/GHCNpy/',
    description='Package for Analyzing and Displaying Weather Stations from GHCN-Daily',
    long_description=open('README.md').read(),
    license='New BSD',
    keywords = "meteorology climatology analysis in_situ",
    scripts=['ghcnpy/iotools.py', 'ghcnpy/metadata.py', 'ghcnpy/plotting.py'],
    data_files = [("", ["LICENSE.txt"])],
    install_requires=[
          'numpy',
          'netcdf4',
          'geopy',
          'requests',
          'matplotlib',
    ],
)
