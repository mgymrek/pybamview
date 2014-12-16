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
import pybamview
import pyfasta
from flask import (request, redirect, render_template, url_for, Response,
                   current_app)
import os
from os.path import join
import re
import socket
import threading
import tempfile
import webbrowser

from .app import create_app
from .utils import message, ParseTargets, random_ports

app = create_app()

NUC_TO_COLOR = {
    "A": "red",
    'a': "red",
    "C": "blue",
    "c": "blue",
    "G": "green",
    "g": "green",
    "T": "orange",
    "t": "orange",
    "N": "gray",
    "n": "gray",
    "-": "white",
    ".": "gray",
}


@app.route('/')
def listsamples(methods=['POST','GET']):
    # If a single file, jump right to the view for that file
    BAM = current_app.config['BAM']
    BAMDIR = current_app.config['BAMDIR']
    if BAM:
        if not os.path.exists(BAM) or not pybamview.CheckBam(BAM):
            return render_template("error.html", message="%s not a valid BAM file"%BAM)
        try:
            samplesToBam = pybamview.GetSamplesFromBamFiles([os.path.abspath(BAM)])
        except ValueError, e:
            return render_template("error.html", message="Problem parsing BAM file: %s"%e, title="PyBamView - %s"%BAM)
        if not os.path.exists(BAM+".bai"):
            return render_template("error.html", message="No index found for %s"%BAM)
        if len(samplesToBam.keys()) == 0:
            return render_template("error.html", message="No samples found in BAM file", title="PyBamView - %s"%BAM)
        argstring = "&".join(["samplebams=%s:%s"%(sample, os.path.abspath(BAM)) for sample in samplesToBam])
        return redirect(url_for("display_bam")+"?"+argstring)
    # If given a directory to look for bams, determine which samples are present
    else:
        bamfiles = request.args.getlist("bamfiles")
        samples = request.args.getlist("samples")
        if len(bamfiles) > 0 and len(samples) > 0:
            return display_bam(samples)
        try:
            files = os.listdir(BAMDIR)
        except OSError: files = []
        bamfiles = [f for f in files if re.match(".*.bam$", f) is not None]
        bamfiles = [f for f in bamfiles if f+".bai" in files]
        try:
            samplesToBam = pybamview.GetSamplesFromBamFiles([os.path.join(os.path.abspath(BAMDIR), b) for b in bamfiles])
        except ValueError, e:
            return render_template("error.html", message="Problem parsing BAM file: %s"%e, title="PyBamView - %s"%BAMDIR)
        return render_template("index.html", samplesToBam=samplesToBam, title="PyBamView - %s"%BAMDIR)


@app.route('/bamview', methods=['POST', 'GET'])
def display_bam():
    samplebams = request.args.getlist("samplebams")
    zoomlevel = request.args.get("zoomlevel")
    if len(samplebams) == 0:
        samples_toinclude = list(set(request.args.getlist("samples")))
        bamfiles_toinclude = list(set(request.args.getlist("bamfiles")))
    else:
        samples_toinclude = []
        bamfiles_toinclude = []
        for s in samplebams:
            samples_toinclude.append(s.split(":")[0])
            for item in s.split(":")[1:]:
                bamfiles_toinclude.extend(item.split(","))
    region = request.args.get("region", pybamview.GetDefaultLocation(bamfiles_toinclude))
    return display_bam_region(list(set(bamfiles_toinclude)), samples_toinclude, region, zoomlevel)


def display_bam_region(bamfiles, samples, region, zoomlevel):
    bamdir = current_app.config["BAMDIR"]
    reffile = current_app.config["REFFILE"]
    settings = current_app.config["SETTINGS"]
    bamfile_to_bamview = current_app.config["BAMFILE_TO_BAMVIEW"]
    if region == "error":
        return render_template("error.html", message="No aligned reads found in the selected BAM files")
    for bam in bamfiles:
        if not os.path.exists(join(bamdir,bam)):
            message("bam file %s does not exist"%join(bamdir, bam), "warning")
    if ";".join(bamfiles) not in bamfile_to_bamview:
        bv = pybamview.BamView([join(bamdir, bam) for bam in bamfiles], reffile)
        bamfile_to_bamview[";".join(bamfiles)] = bv
    else: bv = bamfile_to_bamview[";".join(bamfiles)]
    try:
        chrom, pos = region.split(":")
        pos = int(pos)
    except:
        return render_template("error.html", message="Invalid region specified %s. Region must be of the form chrom:position."%region)
    bv.LoadAlignmentGrid(chrom, pos, _samples=samples, _settings=settings)
    positions = bv.GetPositions(pos)
    region = "%s:%s" % (chrom, pos)
    return render_template("bamview.html",
        title="PyBamView - %s" % region,
        BAM_FILES=bamfiles,
        REF_FILE=reffile,
        REGION=region,
        SAMPLES=bv.GetSamples(),
        SAMPLE_HASHES=bv.GetSampleHashes(),
        BUFFER=settings["NUMCHAR"],
        MAXZOOM=settings["MAXZOOM"],
        ZOOMLEVEL=zoomlevel,
        REFERENCE=bv.GetReferenceTrack(pos),
        ALIGNMENTS=bv.GetAlignmentTrack(pos),
        TARGETPOS=pos,
        POSITIONS=positions,
        NUC_TO_COLOR=NUC_TO_COLOR,
        CHROM=chrom,
        TARGET_LIST=current_app.config.get("TARGET_LIST", [])
    )


@app.route('/snapshot', methods=['POST', 'GET'])
def snapshot():
    settings = current_app.config['SETTINGS']
    samples = request.form.getlist("samples")
    alignments_by_sample = {}
    for s in samples:
        alignments_by_sample[s] = request.form["alignment_%s"%s]
    region = request.form["region"]
    region.replace("%3A",":")
    startpos = request.form["startpos"]
    reference = request.form["reference"]
    zoom = request.form["zoomlevel"]
    zoomlevel = float(zoom)
    if zoomlevel < 0: zoomlevel = -1/zoomlevel
    chrom, start = region.split(":")
    region = "%s-%s"%(max(int(int(start)-25/zoomlevel),0), int(int(start)+50+25/zoomlevel))
    return render_template("snapshot.html", title="Pybamview - take snapshot", SAMPLES=samples, ZOOMLEVEL=zoom, \
                               CHROM=chrom, REGION=region, MINSTART=int(start)-settings["LOADCHAR"]/2, MAXEND=int(start)+settings["LOADCHAR"]/2,\
                               REFERENCE_TRACK=reference, ALIGN_BY_SAMPLE=alignments_by_sample, STARTPOS=startpos)


@app.route('/export', methods=["POST"])
def export():
    svg_xml = request.form.get("data", "Invalid data")
    input_file = tempfile.NamedTemporaryFile(delete=False)
    input_file.write(svg_xml)
    input_file.close()
    filename = request.form.get("filename", "pybamview_snapshot.pdf")
    output_file_name = os.path.join("/tmp", filename)
    cmd = "rsvg-convert -o %s -f pdf %s"%(output_file_name, input_file.name)
    retcode = os.system(cmd)
    if retcode != 0:
        message("Error exporting to PDF. Is rsvg-convert installed?", "warning")
    if os.path.exists(output_file_name):
        pdf_data = open(output_file_name, "r").read()
    else: pdf_data = ""
    response = Response(pdf_data, mimetype="application/x-pdf")
    response.headers["Content-Disposition"] = "attachment; filename=%s"%filename
    return response


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
