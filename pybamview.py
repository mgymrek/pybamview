import argparse
from flask import Flask
from display_html import *
import os
import re
import sys
app = Flask(__name__)
app.debug = True

BAMDIR = "."
REFFILE = ""
PORT = 5000
HOST = "127.0.0.1"

@app.route("/")
def listbams():
    files = os.listdir(BAMDIR)
    bamfiles = [f for f in files if re.match(".*.bam$", f) is not None]
    bamfiles = [f for f in bamfiles if f+".bai" in files]
    html = "<h1>Indexed bam files in this directory</h1>"
    html += "<ul>"
    for f in bamfiles:
        html += "<li><a href='/%s' target='_blank'>%s</a></li>"%(f,f)
    html += "</ul>"
    return html

@app.route('/<string:bamfile>')
def display_bam(bamfile):
    return display_bam_region(bamfile, 0)

@app.route('/<string:bamfile>:<string:region>')
def display_bam_region(bamfile, region):
    html = GetHeader(bamfile, region, REFFILE)
    html += GetToolbar()
    html += GetReference(REFFILE, region)
    html += GetAlignment(bamfile, region, REFFILE)
    html += GetFooter()
    return html

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='pybamview')
    parser.add_argument('--bamdir', help='Directory to look for bam files. Bam files must be indexed.')
    parser.add_argument('--ref', help='Path to reference fasta file. If no reference is given, the reference track is displayed as "N"\'s')
    parser.add_argument('--ip', help='Host IP. 127.0.0.1 for local host (default). 0.0.0.0 to have the server available externally.')
    parser.add_argument('--port', help='The port of the webserver. Defaults to 5000.')
    args = parser.parse_args()
    if args.bamdir is not None:
        BAMDIR = args.bamdir
    if args.ref is not None:
        REFFILE = args.ref
    if args.port is not None:
        PORT = int(args.port)
    if args.ip is not None:
        HOST = args.ip
    app.run(port=PORT, host=HOST)
