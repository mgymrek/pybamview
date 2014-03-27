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

VERSION = '0.0.1'

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
      data_files=[('pybamview/css',['pybamview.css']),
                  ('pybamview/javascript', ['pybamview.js', 'snapshot.js']),
                  ('pybamview/static', ['favicon.ico']),
                  ('pybamview/templates', ['templates/index.html', 'templates/bamview.html',\
                                               'templates/snapshot.html'])],
      scripts=['scripts/pybamview'],
      test_suite='pybamview.tests',
      requires=['argparse','flask','pandas','pyfasta','pysam'],
     )
