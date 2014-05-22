from setuptools import setup

DESCRIPTION = "Python based BAM alignment viewer"
LONG_DESCRIPTION = "Python based BAM alignment viewer. See a running example at http://pybamview.melissagymrek.com/?bamfiles=example.sorted.bam&region=chrY%3A14937824"
NAME = "pybamview"
AUTHOR = "Melissa Gymrek"
AUTHOR_EMAIL = "mgymrek@mit.edu"
MAINTAINER = "Melissa Gymrek"
MAINTAINER_EMAIL = "mgymrek@mit.edu"
DOWNLOAD_URL = 'http://github.com/mgymrek/pybamview'
LICENSE = 'MIT'

VERSION = '0.1.1'

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
                                               'templates/snapshot.html', 'templates/error.html'])],
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
