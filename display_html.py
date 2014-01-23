def GetHeader(bamfile, region, reffile):
    """
    Get header div fo pybamview
    """
    header_html = "<html><head>"
    header_html += "<style type='text/css'>%s</style>"%open("/home/mgymrek/workspace/pybamview/pybamview.css","r").read()
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
    return "<footer>This alignment is being viewed with <a href='https://github.com/mgymrek/pybamview' target='_blank'>PyBamView</a></footer>"

def GetToolbar():
    """
    Get HTML for the toolbar
    """
    toolbar_html = ""
    toolbar_html += "<div>Toolbar options will go here</div>"
    return toolbar_html

def GetReference(reffile, region):
    """
    Get HTML to display the reference sequence
    """
    reference_html = "<div>Reference sequence here</div>"
    return reference_html

def GetAlignment(bamfile, reffile, region):
    """
    Get HTML for the alignment div
    """
    aln_html = ""
    aln_html += "This will show the alignment for bam %s with ref %s at region %s"%(bamfile, reffile, region)
    return aln_html
