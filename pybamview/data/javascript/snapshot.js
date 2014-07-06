// Functions to draw snapshot
$(document).ready(function()
{
    // Draw default when load page
    var region = document.forms["snapform"]["region"].value;
    var frompos = parseInt(region.split("-")[0]);
    var topos = parseInt(region.split("-")[1]);
    var samples=samples;
    var fromindex=frompos-startpos;
    var toindex=topos-startpos;
    var zoomlevel = parseFloat(document.forms["snapform"]["zoomlevel"].value);
    DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, true);
    var samples_subset = [];

    // Redraw if you want to change something
    $("#draw").click
	(
	 function() {
	     samples_subset = [];
	     var region = document.forms["snapform"]["region"].value;
	     if (region.split("-").length != 2) {
		 alert("Invalid region");
		 return;
	     }
	     var frompos = parseInt(region.split("-")[0]);
	     var topos = parseInt(region.split("-")[1]);
	     if (isNaN(frompos)) {
		 alert("Invalid start position");
		 return;
	     }
	     if (isNaN(topos)) {
		 alert("Invalid end position");
		 return;
	     }
	     if (samples.length > 1) {
		 for (var i = 0; i < document.forms["snapform"]["sample"].length; i++) {
		     if (document.forms["snapform"]["sample"][i].checked) {
			 samples_subset = samples_subset.concat(document.forms["snapform"]["sample"][i].value);
		     }
		 }
	     } else {
		 samples_subset = samples;
	     }
	     fromindex=frompos-startpos;
	     toindex=topos-startpos;
	     if (frompos < minstart) {
		 alert("Start position must be at least " + minstart);
		 return;
	     }
	     if (topos > maxend) {
		 alert("End position must be less than " + maxend);
		 return;
	     }
	     if (frompos > topos) {
		 alert("End position must be greater than the start position");
		 return;
	     }
	     DrawSnapshot(reference_track, samples_subset, alignBySample, fromindex, toindex);
	 }
	 );
    
    // Export
    $("#export").click
	(
	 function() {
	     // Get the d3 SVG element
	     var svg = document.getElementById("snapshot").getElementsByTagName("svg")[0];

	     // Extract SVG text string
	     var svg_xml = (new XMLSerializer).serializeToString(svg);
	     
	     // Set filename based on region
	     var start = document.forms["snapform"]["region"].value.split("-")[0];
	     var end = document.forms["snapform"]["region"].value.split("-")[1];
	     var filename = "pybamview_" + chrom + "_" + start + "_" + end + ".pdf";

	     // Make a form with the SVG data
	     var form = document.getElementById("exportform");
	     form['data'].value = svg_xml;
	     form['filename'].value = filename;
	     form.submit();
	 }
	 );
});