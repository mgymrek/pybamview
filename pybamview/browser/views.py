# -*- coding: utf-8 -*-
import os
from os.path import join
import re
import tempfile

import pybamview
from flask import (Blueprint, current_app, redirect, render_template,
                   request, Response, url_for)

from ..utils import message

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

blueprint = Blueprint("browser", __name__, template_folder="templates",
                      static_folder="static")


@blueprint.route('/')
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

        if not (os.path.exists(BAM+".bai") or os.path.exists(BAM.replace(".bam",".bai"))):
            return render_template("error.html", message="No index found for %s"%BAM)
        if len(samplesToBam.keys()) == 0:
            return render_template("error.html", message=
                "No samples found in BAM file. Check read groups are properly assigned.",
                 title="PyBamView - %s"%BAM)
        argstring = "&".join(["samplebams=%s:%s"%(sample, os.path.abspath(BAM)) for sample in samplesToBam])
        return redirect(url_for(".display_bam")+"?"+argstring)
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
        bamfiles = [f for f in bamfiles if ((f+".bai") in files or \
                f.replace(".bam",".bai") in files)]
        try:
            samplesToBam = pybamview.GetSamplesFromBamFiles([os.path.join(os.path.abspath(BAMDIR), b) for b in bamfiles])
        except ValueError, e:
            return render_template("error.html", message="Problem parsing BAM file: %s"%e, title="PyBamView - %s"%BAMDIR)
        return render_template("index.html", samplesToBam=samplesToBam, title="PyBamView - %s"%BAMDIR)

@blueprint.route('/bamview', methods=['POST', 'GET'])
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
    else:
        bv = bamfile_to_bamview[";".join(bamfiles)]
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


@blueprint.route('/snapshot', methods=['POST', 'GET'])
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
    if zoomlevel < 0:
        zoomlevel = -1/zoomlevel
    chrom, start = region.split(":")
    region = "%s-%s"%(max(int(int(start)-25/zoomlevel),0), int(int(start)+50+25/zoomlevel))
    return render_template("snapshot.html", title="Pybamview - take snapshot", SAMPLES=samples, ZOOMLEVEL=zoom, \
                               CHROM=chrom, REGION=region, MINSTART=int(start)-settings["LOADCHAR"]/2, MAXEND=int(start)+settings["LOADCHAR"]/2,\
                               REFERENCE_TRACK=reference, ALIGN_BY_SAMPLE=alignments_by_sample, STARTPOS=startpos)


@blueprint.route('/export', methods=["POST"])
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
