# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2014 Melissa Gymrek <mgymrek@mit.edu>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import optparse
import errno
import pyfasta
import os
import socket
import threading
import webbrowser

from .app import create_app
from .utils import message, ParseTargets, random_ports


def parse_args():
    parser = optparse.OptionParser(description='pybamview: An Python-based BAM alignment viewer.')
    parser.add_option('--bam', help='Run Pybamview on this BAM file only. The file must be indexed.', type='string')
    parser.add_option('--bamdir', help='Directory to look for bam files. Bam files must be indexed.', type='string')
    parser.add_option('--ref', help='Path to reference fasta file. If no reference is given, the reference track is displayed as "N"\'s', type='string')
    parser.add_option('--ip', help='Host IP. 127.0.0.1 for local host (default). 0.0.0.0 to have the server available externally.', type='string', default="127.0.0.1")
    parser.add_option('--port', help='The port of the webserver. Defaults to 5000.', type='int', default=5000)
    parser.add_option('--targets', help='Bed file with chrom, start, end, and name. Allows you to easily jump to these targets.', type='string')
    parser.add_option('--buffer', help='How many nucleotides to load into memory. Default: 200. Buffering more allows you to scroll farther. Buffering less is faster.', \
                            type='int', default=200)
    parser.add_option("--maxzoom", help="Maximum number of times to be able to zoom out. E.g. --maxzoom 10 allows zooming out up to 10x. Default: 100. Must be between one of 1-10, 50, or 100.", type='int', default=100)
    parser.add_option('--no-browser', help="Don't automatically open the web browser.", action="store_true")
    parser.add_option('--debug', help='Run PyBamView in Flask debug mode', action="store_true")

    return parser.parse_args()


def cli():
    """Launch command line interface."""
    # Get command line args and options
    (options, args) = parse_args()

    if not options.bamdir and not options.bam:
        message('You must specify either a bam file (--bam) or a directory to look for bam files (--bamdir)', "error")

    if options.bamdir and options.bam:
        message('You must specify only one of --bam or --bamdir', "error")

    app = create_app()

    app.config["BAM"] = options.bam
    app.config["BAMDIR"] = options.bamdir
    app.config["REFFILE"] = REFFILE = options.ref
    HOST = options.ip
    PORT = options.port
    TARGETFILE = options.targets
    NUMCHAR = options.buffer
    MAXZOOM = options.maxzoom
    if MAXZOOM not in range(1,11) + [50, 100]:
        message("Must set --maxzoom to one of 1-10, 50, or 100", "error")
    app.debug = options.debug
    OPEN_BROWSER = (not options.no_browser)

    app.config["BAMFILE_TO_BAMVIEW"] = {}
    app.config["PORT_RETRIES"] = 50
    app.config["SETTINGS"] = {
        "NUMCHAR": NUMCHAR,
        "MAXZOOM": MAXZOOM,
        "LOADCHAR": NUMCHAR * MAXZOOM
    }

    # Load reference
    if REFFILE is None:
        REFFILE = "No reference loaded"
    elif not os.path.exists(REFFILE):
        message("Could not find reference file %s"%REFFILE, "warning")
        REFFILE = "Could not find reference file %s"%REFFILE
    else:
        try:
            _ = pyfasta.Fasta(REFFILE) # Make sure we can open the fasta file
        except:
            message("Invalid reference fasta file %s"%REFFILE, "warning")
            REFFILE = "Invalid fasta file %s"%REFFILE

    # Parse targets
    if TARGETFILE is not None:
        if not os.path.exists(TARGETFILE):
            message("Target file %s does not exist"%TARGETFILE, "warning")
            TARGETFILE = None
        else:
            app.config['TARGET_LIST'] = ParseTargets(TARGETFILE)

    # Start app
    success = False
    for port in random_ports(PORT, app.config["PORT_RETRIES"] + 1):
        try:
            if OPEN_BROWSER:
                url = "http://%(host)s:%(port)s" % dict(host=HOST, port=port)
                threading.Timer(1.5, lambda: webbrowser.open(url)).start()
            app.run(host=HOST, port=port)
            success = True
        except webbrowser.Error as e:
            message("No web browser found: %s."%e, "warning")
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                message("Port %s is already in use. Trying another port"%port, "warning")
                continue
            elif e.errno in (errno.EACCES, getattr(errno, "WSEACCES", errno.EACCES)):
                message("Permission denied to listen on port %s. Trying another port"%port, "warning")
                continue
            else: raise
        except OverflowError:
            message("Invalid port specified (%s)."%port, "error")
        else: break
    if not success:
        message("PyBamView could not find an available port. Quitting", "error")
