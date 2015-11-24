from setuptools import setup, find_packages

DESCRIPTION = "Python based BAM alignment viewer"
LONG_DESCRIPTION = DESCRIPTION
NAME = "pybamview"
AUTHOR = "Melissa Gymrek"
AUTHOR_EMAIL = "mgymrek@mit.edu"
MAINTAINER = "Melissa Gymrek"
MAINTAINER_EMAIL = "mgymrek@mit.edu"
DOWNLOAD_URL = 'http://github.com/mgymrek/pybamview'
LICENSE = 'MIT'

VERSION = '1.0.7'

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=DOWNLOAD_URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=find_packages(exclude=('examples')),
      package_data={
        'pybamview': ['browser/static/css/*.css',
                      'browser/static/img/*',
                      'browser/static/javascript/*.js',
                      'browser/templates/*.html',
                      'snapshot.js',
                      'tests/data/*']
      },
      test_suite='pybamview.tests',
      entry_points={
        'console_scripts': [
          'pybamview = pybamview.cli:cli',
          'snapbam = pybamview.snapshot:cli',
        ],
      },
      install_requires=['flask','pyfasta','pysam'],
      classifiers=['Development Status :: 4 - Beta',\
                       'Programming Language :: Python :: 2.6',\
                       'License :: OSI Approved :: MIT License',\
                       'Operating System :: OS Independent',\
                       'Intended Audience :: Science/Research',\
                       'Topic :: Scientific/Engineering :: Bio-Informatics',\
                       'Topic :: Scientific/Engineering :: Visualization']
     )
