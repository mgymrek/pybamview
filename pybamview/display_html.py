import sys
CSS_PREFIX = sys.prefix + "/pybamview/css"
JS_PREFIX = sys.prefix + "/pybamview/javascript"
NUMCHARS = 120 # how many characters to display at once

def GetHeader(bamfiles, region, minpos, maxpos, reffile, samples):
    """
    Get header div fo pybamview
    """
    try:
        chrom, position = region.split(":")
    except: chrom, position = "chr1", 0
    header_html = "<head>"
    header_html += "<link rel='shortcut icon' href='/favicon.ico'>"
    header_html += "<style type='text/css'>%s</style>"%open("%s/pybamview.css"%CSS_PREFIX,"r").read()
    header_html += "<script src=\"//ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js\"></script>"
    header_html += "<script language=javascript type='text/javascript'>var NUMSAMPLES=%s;var NUMCHARS=%s;var currentpos=%s;var minpos=%s;var maxpos=%s;var chrom=\"%s\";\n%s</script>"\
        %(len(samples),NUMCHARS,position,minpos,maxpos-NUMCHARS,chrom,open("%s/pybamview.js"%JS_PREFIX,"r").read())
    header_html += "<title>PyBamView: %s</title>"%",".join(bamfiles)
    header_html += "</head>"
    header_html += "<div class='fixedElement'>" # begin fixed
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
    header_html += "<div id='param_info'>Keyboard commands: [left],[right] scroll by one, [space],[backspace] scroll by 10</div>"
    header_html += "</div></header>"
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
def GetReference(reference_string, chrom, pos, positions):
    """
    Get HTML to display the reference sequence
    """
    min_pos = pos
    max_pos = pos + NUMCHARS
    reference_html = "<div class='reference'>"
    reference_html += "<table>"
    reference_html += "<tr>"
    for i in range(len(reference_string)):
        color = NUC_TO_COLOR.get(reference_string[i], "gray")
        display = ""
        if positions[i] < min_pos or positions[i] > max_pos: display = "display:none;"
        reference_html += "<td class='%s_%s' style='background-color:%s;%s'><font class='ref'><b>%s</b></font></div></td>"%(chrom, positions[i], color, display, reference_string[i])
    reference_html += "</tr>"
    reference_html += "</table></div>"
    reference_html += "</div>" # end fixed
    return reference_html

def GetAlignment(alignments_by_sample, numcols, chrom, pos, positions):
    """
    Get HTML for the alignment div
    """
    min_pos = pos
    max_pos = pos + NUMCHARS
    aln_html = "<div class='alignments'>"
    for sample in alignments_by_sample:
        aln_html += "<a name='%s'></a>"%sample
        aln_html += "<div style='background-color:lightgray;' onclick='toggleDiv(\"%s\");'>%s (show/hide)</div>"%(sample, sample)
        aln_html += "<div id='%s' style:'background-color:red;'>"%sample
        aln_html += "<table>"
        alignment_list = alignments_by_sample[sample]
        for aln in alignment_list:
            aln_html += "<tr>"
            for i in range(len(aln)):
                color = NUC_TO_COLOR.get(aln[i], "black")
                display = ""
                if positions[i] < min_pos or positions[i] > max_pos: display = "display:none;"
                aln_html += "<td class='%s_%s' style='text-align:center;%s'><font class='read' color='%s'>%s</font></td>"%(chrom, positions[i], display, color, aln[i])
            aln_html += "</tr>"
        aln_html += "</table>"
        aln_html += "</div><br>"
    aln_html += "</div>"
    return aln_html
