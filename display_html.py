def GetHeader(bamfiles, region, reffile, samples):
    """
    Get header div fo pybamview
    """
    header_html = "<html><head>"
    header_html += "<style type='text/css'>%s</style>"%open("/san/melissa/workspace/pybamview/pybamview.css","r").read()
    header_html += "<script src=\"//ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js\"></script>"
    header_html += "<script language=javascript type='text/javascript'>%s</script>"%open("/san/melissa/workspace/pybamview/pybamview.js","r").read()
    header_html += "<title>PyBamView: %s</title>"%",".join(bamfiles)
    header_html += "<div class='outer' id='header_wrap'>"
    header_html += "<header class='inner'>"
    header_html += "<h1 id='display_info'>PyBamView</h1>"
    header_html += "<div id='param_info'>Bam file: %s</div>"%",".join(bamfiles)
    header_html += "<div id='param_info'>Reference: %s</div>"%reffile
    header_html += "<div id='param_info'>Region: %s</div>"%region
    header_html += "<div id='param_info'>Samples:<br>"
    for sample in samples:
        header_html += "<a href='#%s'><font color='white'>%s</font></a> "%(sample, sample)
    header_html += "</div>"
    header_html += "</header>"
    header_html += "</div></head>"
    return header_html

def GetFooter():
    """
    Get footer div for pybamview
    """
    return "<div id='footer_wrap' class='outer'><footer class='inner'><div id='footer_info'>This alignment is being viewed with <a href='https://github.com/mgymrek/pybamview' target='_blank'>PyBamView</a></div></footer></div>"

def GetToolbar(chrom, pos, bamfiles, settings):
    """
    Get HTML for the toolbar
    """
    toolbar_html = "<div class ='outer' id='toolbar'>"
    toolbar_html += "<form>"
    for bam in bamfiles:
        toolbar_html += "<input type='hidden' name='bamfiles', value='%s'>"%bam
    toolbar_html += "Enter region: <input type='text' name='region' value=%s>"%settings["region"]
    toolbar_html += "<input type='submit'>"
    toolbar_html += "<div id='selected'>Selected: </div>"
    toolbar_html += "</form>"
    toolbar_html += "</div>"
    return toolbar_html

NUC_TO_COLOR = {
    "A": "red",
    'a': "red",
    "C": "blue",
    "c": "blue",
    "G": "green",
    "g": "green",
    "T": "orange",
    "t": "orange"
}
def GetReference(reference_string, chrom, positions):
    """
    Get HTML to display the reference sequence
    """
    reference_string
    reference_html = "<table>"
    reference_html += "<tr>"
    for i in range(len(reference_string)):
        color = NUC_TO_COLOR.get(reference_string[i], "gray")
        reference_html += "<td class='%s_%s' style='background-color:%s;'><font class='ref'><b>%s</b></font></div></td>"%(chrom, positions[i], color,reference_string[i])
    reference_html += "</tr></table>"
    return reference_html

def GetAlignment(alignments_by_sample, numcols, chrom, positions):
    """
    Get HTML for the alignment div
    """
    aln_html = ""
    for sample in alignments_by_sample:
        aln_html += "<div style='background-color:lightgray;' onclick='toggleDiv(\"%s\");'><a name='%s'>%s</a></div>"%(sample, sample, sample)
        aln_html += "<div id='%s' style:'background-color:red;'>"%sample
        aln_html += "<table>"
        alignment_list = alignments_by_sample[sample]
        for aln in alignment_list:
            aln_html += "<tr>"
            for i in range(len(aln)):
                color = NUC_TO_COLOR.get(aln[i], "black")
                aln_html += "<td class='%s_%s' style='text-align:center;'><font class='read' color='%s'>%s</font></td>"%(chrom, positions[i], color, aln[i])
            aln_html += "</tr>"
        aln_html += "</table>"
        aln_html += "</div><br>"
    return aln_html
