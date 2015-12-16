pybamview
=========

Browser based application for viewing bam alignments

The website is [here](http://melissagymrek.com/pybamview/) and contains full usage instructions, an faq, and a served example.

Copyright (c) 2014 Melissa Gymrek <mgymrek@mit.edu>

LICENSE: MIT (see LICENSE.txt)

Requirements
==========
PyBamView requires Python2.6 or greater. The following python packages are required:

* ```Flask```
* ```pysam```
* ```pyfaidx```

These can all be installed using ```pip``` or ```easy_install```. Additionally, the package ```rsvg-convert``` is required for exporting alignment snapshots to PDF.

Installation
==========

PyBamView can be easily installed using pip: ```pip install pybamview```

To install from source, download or clone the package from github, ensure the required packages are installed, and run ```python setup.py install``` from the root directory of the pybamview package.

Usage
===========

To use PyBamView, you will need a directory containing indexed BAM files, and optionally a reference genome. All reads in the BAM files must be annotated with a read group. To run, type the command:

```pybamview --bamdir $BAMDIR --ref $REF.FA```

This will serve pybamview at http://127.0.0.1:5000. Navigate to this URL at your web browser, where you can select samples and start visualizing alignments. Use the ```--ip``` and ```--port``` to change the host URL and port if desired.
