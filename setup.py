from setuptools import setup, find_packages

setup(
    name='GHCNpy',
    version='1.0',
    author='Jared Rennie, Samuel Lillo',
    author_email='jared@cicsnc.org, splillo@ou.edu',
    packages=find_packages(),
    url='https://github.com/',
    description='Package for Analyzing and Displaying weather stations from GHCN-Daily',
    long_description=open('README.md').read(),
    license='New BSD',
    keywords = "meteorology climatology analysis in_situ"
    #scripts=['bin/example', 'bin/sync_surveys'],
    #data_files = [("", ["LICENSE.txt"])],
    #install_requires=[
    #    "requests >= 2.1.0",
    #    "python-dateutil >= 2.2",
    #    "PyYAML >= 3.11",
    #    "beautifulsoup4 >= 4.3.2",
    #    "pytest >= 2.5.2"
    #],
    #cmdclass={'test': PyTest},
)
