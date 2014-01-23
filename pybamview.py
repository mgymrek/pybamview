import argparse
from flask import Flask
import os
import re
import sys
app = Flask(__name__)
app.debug = True

BAMDIR = ""
REFFILE = ""

@app.route("/")
def listbams():
    if BAMDIR == "":
        files = os.listdir(".")
    else: files = os.listdir(BAMDIR)
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
    return "this will show the alignment for bam %s with reference %s at region %s"%(bamfile, REFFILE, region)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='pybamview')
    parser.add_argument('--bamdir', help='Directory to look for bam files. Bam files must be indexed.')
    parser.add_argument('--ref', help='Path to reference fasta file. If no reference is given, the reference track is displayed as "N"\'s')
    args = parser.parse_args()
    BAMDIR = args.bamdir
    REFFILE = args.ref
    app.run()
