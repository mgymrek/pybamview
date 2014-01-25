def GetHeader(bamfile, region, reffile):
    """
    Get header div fo pybamview
    """
    header_html = "<html><head>"
    header_html += "<style type='text/css'>%s</style>"%open("/san/melissa/workspace/pybamview/pybamview.css","r").read()
    header_html += "<title>PyBamView: %s</title>"%bamfile
    header_html += "<div class='outer' id='header_wrap'>"
    header_html += "<header class='inner'>"
    header_html += "<h1 id='display_info'>PyBamView</h1>"
    header_html += "<div id='param_info'>Bam file: %s</div>"%bamfile
    header_html += "<div id='param_info'>Reference: %s</div>"%reffile
    header_html += "<div id='param_info'>Region: %s</div>"%region
    header_html += "</header>"
    header_html += "</div></head>"
    return header_html

def GetFooter():
    """
    Get footer div for pybamview
    """
    return "<div id='footer_wrap' class='outer'><footer class='inner'><div id='footer_info'>This alignment is being viewed with <a href='https://github.com/mgymrek/pybamview' target='_blank'>PyBamView</a></div></footer></div>"

def GetToolbar(chrom, pos, settings):
    """
    Get HTML for the toolbar
    """
    toolbar_html = "<div class ='outer' id='toolbar'>"
    toolbar_html += "<form>"
    toolbar_html += "Enter region: <input type='text' name='region' value=%s>"%settings["region"]
    toolbar_html += "<input type='submit'>"
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
def GetReference(reference_string):
    """
    Get HTML to display the reference sequence
    """
    reference_html = "<tr>"
    for i in range(len(reference_string)):
        color = NUC_TO_COLOR.get(reference_string[i], "gray")
        reference_html += "<td style='background-color:%s;text-align:center;text-valign:center;'><font color='white'><b>%s</b></font></td>"%(color,reference_string[i])
    reference_html += "</tr>"
    return reference_html

def GetAlignment(alignment_list):
    """
    Get HTML for the alignment div
    """
    aln_html = ""
    for aln in alignment_list:
        aln_html += "<tr>"
        for i in range(len(aln)):
            color = NUC_TO_COLOR.get(aln[i], "black")
            aln_html += "<td style='text-align:center;'><font color='%s'>%s</font></td>"%(color, aln[i])
        aln_html += "</tr>"
    return aln_html
