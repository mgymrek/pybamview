// Functions to draw snapshot

function IsNuc(x) {
    return (x=="A" || x=="C" || x=="G" || x=="T");
}

function DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex) {
    // Reset
    document.getElementById("snapshot").innerHTML = "";

    // Set positioning variables
    gridWidth = 15;
    gridHeight = 20;
    var numreads = 0;
    for (var i =0; i < samples.length; i++) {
	numreads += alignBySample[samples[i]].split(";").length;
    }
    var w = gridWidth*(toindex-fromindex+1);
    var h = (1+samples.length*2+numreads)*gridHeight;

    // Set up colors
    var colors = {
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
    };

    // Put SVG element in #snapshot
    var svg = d3.select("#snapshot").append("svg:svg")
	.attr("width", w)
	.attr("height", h);

    // Draw reference
    var refdata = reference_track.slice(fromindex, toindex+1).split("");
    var RefTrack = svg.selectAll("gref")
	.data(refdata)
	.enter().append("g");
    RefTrack.append("rect")
	.attr("x", function(d, i) { return i*gridWidth; })
	.attr("y", 0)
	.attr("width", gridWidth)
	.attr("height", gridHeight)
	.style("fill", function(d) {return colors[d];})
	.style("stroke", "white");
    RefTrack.append("text")
	.attr("x", function(d, i) {return i*gridWidth+gridWidth/2; })
	.attr("y", gridHeight/2)
	.attr("dy", ".25em")
	.attr("fill", "white")
	.style("font-family", "Courier")
	.style("text-anchor", "middle")
	.text(function(d) {return d;});

    // Draw each sample
    var currentHeight = gridHeight*1.6;
    for (var i=0; i < samples.length; i++) {
	// Append sample label
	svg.append("text")
	    .text(samples[i])
	    .attr("x", 1)
	    .attr("y", currentHeight+gridHeight/2)
	    .attr("dy","0.25em")
	    .attr("fill","black")
	    .style("font-family", "Courier")
	    .style("font-size", "20px")
	    .style("stroke-width", "3px");
	// Draw reads
	currentHeight += gridHeight;
	sample_data = alignBySample[samples[i]];
	sample_data_reads = sample_data.split(";");
	for (var j = 0; j < sample_data_reads.length; j++) {
	    readdata = sample_data_reads[j].slice(fromindex, toindex+1).split("");
	    var SampleTrack = svg.selectAll("gsamp_"+samples[i])
		.data(readdata)
		.enter().append("g");
	    SampleTrack.append("rect")
		.attr("x", function(d, pos) { return pos*gridWidth; })
		.attr("y", currentHeight)
		.attr("width", gridWidth)
		.attr("height", gridHeight)
		.style("fill", function(d, pos) {return (d.toUpperCase()!=refdata[pos].toUpperCase() &&
							 IsNuc(refdata[pos].toUpperCase()) && 
							 IsNuc(d.toUpperCase()))?"yellow":"white";});
	    SampleTrack.append("text")
		.text(function(d) {return d;})
		.attr("x", function(d, pos) {return pos*gridWidth+gridWidth/2;})
		.attr("y", currentHeight + gridHeight/2)
		.attr("dy", ".25em")
		.style("font-family", "Courier")
		.style("text-anchor", "middle")
		.attr("fill", function(d) {return colors[d];});
	    currentHeight += gridHeight;
	}
	// Update position
	currentHeight += gridHeight*1.5;
    }
}

$(document).ready(function()
{
    // Draw default when load page
    var region = document.forms["snapform"]["region"].value;
    var frompos = parseInt(region.split("-")[0]);
    var topos = parseInt(region.split("-")[1]);
    samples=samples;
    fromindex=frompos-startpos;
    toindex=topos-startpos;
    DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex);
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