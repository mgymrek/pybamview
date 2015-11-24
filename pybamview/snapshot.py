# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2015 Melissa Gymrek <mgymrek@mit.edu>

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

import errno
import optparse
import os
import pybamview
import shutil
import sys
import tempfile

JSPATH = os.path.join(os.path.dirname(pybamview.__file__), "browser/static/javascript/")
SSPATH = os.path.dirname(pybamview.__file__)

from .utils import message, ParseTargets, WriteParamFile, RunCommand, CheckProgram, CheckNodeJSPackage

def parse_args():
    parser = optparse.OptionParser(description='Automated generation of pybamview snapshots')
    parser.add_option('--bam', help='Run Pybamview on this BAM file only. The file must be indexed.', type='string')
    parser.add_option('--bamdir', help='Directory to look for bam files. Bam files must be indexed.', type='string')
    parser.add_option('--ref', help='Path to reference fasta file. If no reference is given, the reference track is displayed as "N"\'s', type='string')
    parser.add_option('--regions', help='Bed file with alignment regions to display. Columns: chrom, start, end, name', type='string')
    parser.add_option('--zoom', help='Zoom level (Options: 1-10, 50, 100)', type='int', default=1)
    parser.add_option('--samples', help='Comma-separated list of samples to display', type='string')
    parser.add_option('--outdir', help='Directory to write output', type='string')
    parser.add_option('--buffer', help='Include this many nucleotides buffer upstream and downstream. Between 0-500.', type='int', default=0)
    parser.add_option('--filetype', help='Filetype of snapshots. Options: svg, pdf, html', type='string', default='svg')
    parser.add_option("--downsample",
                      help="Downsample reads to this maximum coverage level. "
                           "Default: 50. Values over 100 not recommended "
                           "since it results in poor performance.",
                      type='int', default=50)
    parser.add_option('--debug', help='Run PyBamView in Flask debug mode', action="store_true")

    return parser.parse_args()


def cli():
    """Launch command line interface."""
    # Get command line args and options
    (options, args) = parse_args()

    # Check for node and required packages
    if not CheckProgram("node"):
        message('Could not find node. Is node installed and in the $PATH?', 'error')
    for package in ["d3","jsdom"]:
        if not CheckNodeJSPackage(package):
            message('Could not fine node.js package %s. Is it installed?' % package)

    # Check options
    if not options.bamdir and not options.bam:
        message('You must specify either a bam file (--bam) or a directory to look for bam files (--bamdir)', "error")
    if options.bamdir and options.bam:
        message('You must specify only one of --bam or --bamdir', "error")
    if options.downsample <= 0:
        message("Must set --downsample to be greater than 0", "error")
    if options.downsample > 100:
        message("Setting --downsample to >100 may result in poor performance", "warning")
    if options.buffer < 0 or options.buffer > 500:
        message("--buffer must be between 0-500", "error")
    if options.regions is None:
        message("Must supply a regons file", "error")
    elif not os.path.exists(options.regions):
        message("Could not fine regions file %s" % options.regions, "error")

    ref_file = None
    if options.ref is not None:
        if not os.path.exists(options.ref):
            message("Could not find reference file %s" % ref_file, "warning")
            ref_file = None
        else:
            try:
                ref_file = options.ref
            except:
                message("Invalid reference fasta file %s" % ref_file, "warning")
                ref_file = None

    # Set up bam viewer
    if options.bam:
        bamfiles = [options.bam]
        bamdir = os.path.dirname(os.path.basename(options.bam))
    else:
        bamdir = options.bamdir
        try:
            files = os.listdir(options.bamdir)
        except OSError: files = []
        bamfiles = [f for f in files if re.match(".*.bam$", f) is not None]
        bamfiles = [f for f in bamfiles if f+".bai" in files]
    bv = pybamview.BamView([os.path.join(bamdir, bam) for bam in bamfiles], ref_file)
    # settings
    settings = {
        "NUMCHAR": 200,
        "MAXZOOM": 100,
        "LOADCHAR": 200 * 100,
        "DOWNSAMPLE": 50,
    }
    samples = options.samples.split(",")
    # Get list of targets
    regions = ParseTargets(options.regions)
    tmpdir = tempfile.mkdtemp()
    for region in regions:
        message("Processing %s" % region["name"])
        chrom, start, end = region["coords"]
        start = start - options.buffer
        end = end + options.buffer 
        minstart = start - settings["LOADCHAR"]/2
        maxend = start + settings["LOADCHAR"]/2
        # Check coords
        if start < minstart:
            message("Start position must be at least %s" % minstart, "error")
        if end > maxend:
            message("End position must be less than %s" % maxend, "error")
        if start > end:
            message("End position must be greater than the start position", "error")

        # Load alignment data
        bv.LoadAlignmentGrid(chrom, start, _samples=samples, _settings=settings)
        alignments = bv.GetAlignmentTrack(start)

        # Get snapshot params
        reference_track = bv.GetReferenceTrack(start)
        alignments = bv.GetAlignmentTrack(start)
        sample_names = bv.GetSamples()
        sample_hashes = bv.GetSampleHashes()
        startpos = bv.GetPositions(start)[0]
        alignments_by_sample = {}
        for i in range(len(sample_names)):
            alignments_by_sample[sample_names[i]] = ";".join(alignments[sample_hashes[i]])
        fromindex = bv.GetIndex(start)
        toindex = bv.GetIndex(end-1)
        # Print params
        paramfile = os.path.join(tmpdir, "params.js")
        WriteParamFile(paramfile, JSPATH, options.filetype, reference_track, samples, alignments_by_sample, fromindex, toindex)

        # Exexute node.js script
        if options.filetype != "pdf":
            cmd = "node %s %s > %s" % \
                (os.path.join(SSPATH, "snapshot.js"), paramfile, \
                        os.path.join(options.outdir, "%s.%s"%(region["name"].replace("/","-"), options.filetype)))
        else:
            cmd = "node %s %s > %s; rsvg-convert %s -f pdf > %s" % \
                (os.path.join(SSPATH, "snapshot.js"), paramfile, os.path.join(tmpdir, "tmp.svg"), \
                    os.path.join(tmpdir, "tmp.svg"), os.path.join(options.outdir, "%s.pdf"%region["name"].replace("/","-")))
        RunCommand(cmd)
    shutil.rmtree(tmpdir)