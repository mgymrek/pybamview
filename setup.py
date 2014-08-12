from setuptools import setup

DESCRIPTION = "Python based BAM alignment viewer"
LONG_DESCRIPTION = DESCRIPTION
NAME = "pybamview"
AUTHOR = "Melissa Gymrek"
AUTHOR_EMAIL = "mgymrek@mit.edu"
MAINTAINER = "Melissa Gymrek"
MAINTAINER_EMAIL = "mgymrek@mit.edu"
DOWNLOAD_URL = 'http://github.com/mgymrek/pybamview'
LICENSE = 'MIT'

VERSION = '1.0.4'

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
      packages=['pybamview'],
      package_dir={'pybamview': 'pybamview'},
      package_data={'pybamview': ['data/css/*.css', 'data/javascript/*.js', 'data/static/*.ico', 'data/static/*.png', 'data/templates/*.html']},
      scripts=['scripts/pybamview'],
      test_suite='pybamview.tests',
      install_requires=['argparse','flask','pandas','pyfasta','pysam'],
      classifiers=['Development Status :: 4 - Beta',\
                       'Programming Language :: Python :: 2.7',\
                       'License :: OSI Approved :: MIT License',\
                       'Operating System :: OS Independent',\
                       'Intended Audience :: Science/Research',\
                       'Topic :: Scientific/Engineering :: Bio-Informatics',\
                       'Topic :: Scientific/Engineering :: Visualization']
     )
