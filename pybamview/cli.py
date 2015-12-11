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
import pyfaidx
import os
import socket
import threading
import webbrowser

from .app import create_app
from .settings import DefaultConfig
from .utils import message, ParseTargets, random_ports


def parse_args():
    parser = optparse.OptionParser(description='pybamview: An Python-based BAM alignment viewer.')
    parser.add_option('--bam', help='Run Pybamview on this BAM file only. The file must be indexed.', type='string')
    parser.add_option('--bamdir', help='Directory to look for bam files. Bam files must be indexed.', type='string')
    parser.add_option('--ref', help='Path to reference fasta file. If no reference is given, the reference track is displayed as "N"\'s', type='string')
    parser.add_option('--ip', help='Host IP. 127.0.0.1 for local host (default). 0.0.0.0 to have the server available externally.', type='string', default="127.0.0.1")
    parser.add_option('--port', help='The port of the webserver. Defaults to 5000.', type='int', default=5000)
    parser.add_option('--targets', help='Bed file with chrom, start, end, and name. Allows you to easily jump to these targets.', type='string')
    parser.add_option('--buffer',
                      help="How many nucleotides to load into memory. "
                           "Default: 200. Buffering more allows you to "
                           "scroll farther. Buffering less is faster.",
                      type='int', default=DefaultConfig.SETTINGS["NUMCHAR"])
    parser.add_option("--maxzoom",
                      help="Maximum number of times to be able to zoom out. "
                           "E.g. --maxzoom 10 allows zooming out up to 10x. "
                           "Default: 100. Must be between one of 1-10, 50, "
                           "or 100.", 
                      type='int', default=DefaultConfig.SETTINGS["MAXZOOM"])
    parser.add_option("--downsample",
                      help="Downsample reads to this maximum coverage level. "
                           "Default: 50. Values over 100 not recommended "
                           "since it results in poor performance.",
                      type='int', default=DefaultConfig.SETTINGS["DOWNSAMPLE"])
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

    host = options.ip
    default_port = options.port

    config = DefaultConfig()
    config.DEBUG = options.debug
    config.BAM = options.bam
    config.BAMDIR = options.bamdir
    config.REFFILE = ref_file = options.ref
    config.SETTINGS = {
        "NUMCHAR": options.buffer,
        "MAXZOOM": options.maxzoom,
        "LOADCHAR": options.buffer * options.maxzoom,
        "DOWNSAMPLE": options.downsample
    }

    if options.maxzoom not in range(1,11) + [50, 100]:
        message("Must set --maxzoom to one of 1-10, 50, or 100", "error")
    if options.downsample <= 0:
        message("Must set --downsample to be greater than 0", "error")
    if options.downsample > 100:
        message("Setting --downsample to >100 may result in poor performance", "warning")
    OPEN_BROWSER = (not options.no_browser)

    # Load reference
    if ref_file is None:
        config.REFFILE = "No reference loaded"
    elif not os.path.exists(ref_file):
        message("Could not find reference file %s" % ref_file, "warning")
        config.REFFILE = "Could not find reference file %s" % ref_file
    else:
        try:
            _ = pyfaidx.Fasta(ref_file) # Make sure we can open the fasta file
        except pyfaidx.FastaIndexingError:
            message("Invalid reference fasta file %s" % ref_file, "warning")
            config.REFFILE = "Invalid fasta file %s" % ref_file

    # Parse targets
    target_file = options.targets
    if target_file is not None:
        if not os.path.exists(target_file):
            message("Target file %s does not exist" % target_file, "warning")
        else:
            config.TARGET_LIST = ParseTargets(target_file)

    # Start app
    app = create_app(config_object=config)
    success = False
    for port in random_ports(default_port, app.config["PORT_RETRIES"] + 1):
        try:
            if OPEN_BROWSER:
                url = "http://%(host)s:%(port)s" % dict(host=host, port=port)
                threading.Timer(1.5, lambda: webbrowser.open(url)).start()
            app.run(host=host, port=port)
            success = True
        except webbrowser.Error as e:
            message("No web browser found: %s." % e, "warning")
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                message("Port %s is already in use. Trying another port" % port, "warning")
                continue
            elif e.errno in (errno.EACCES, getattr(errno, "WSEACCES", errno.EACCES)):
                message("Permission denied to listen on port %s. Trying another port" % port, "warning")
                continue
            else: raise
        except OverflowError:
            message("Invalid port specified (%s)." % port, "error")
        else: break
    if not success:
        message("PyBamView could not find an available port. Quitting", "error")
