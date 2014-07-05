function IsNuc(x) {
    return (x=="A" || x=="C" || x=="G" || x=="T");
}

function InHover(i) {
    // Update color
    d3.selectAll(".p"+i).style("fill","pink");
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected: " + chrom + ":" + i;
}

function OutHover(i) {
    // Update color
    d3.selectAll(".p"+i).style("fill","white");
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected ";
}


function DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex) {
    // Set positioning variables
    gridWidth = 15;
    gridHeight = 20;
    var numreads = 0;
    for (var i =0; i < samples.length; i++) {
	numreads += alignBySample[samples[i]].split(";").length;
    }
    var w = gridWidth*(toindex-fromindex+1);

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

    // Put SVG element for ref track in #alntables
    var refsvg = d3.select("#reference").append("svg:svg")
	.attr("width", w)
	.attr("height", gridHeight);

    // Draw reference
    var refdata = reference_track.slice(fromindex, toindex+1).split("");
    var RefTrack = refsvg.selectAll("gref")
	.data(refdata)
	.enter().append("g");
    RefTrack.append("rect")
	.attr("x", function(d, i) { return i*gridWidth; })
	.attr("y", 0)
	.attr("width", gridWidth)
	.attr("height", gridHeight)
	.attr("id", function(d, i) {return "ref"+i;})
	.style("fill", function(d) {return colors[d];})
	.style("stroke", "white");
    RefTrack.append("text")
	.attr("x", function(d, i) {return i*gridWidth+gridWidth/2; })
	.attr("y", gridHeight/2)
	.attr("dy", ".25em")
	.attr("fill", "white")
	.on("mouseover", function(d,i) {InHover(positions[i]);})
	.on("mouseout", function(d,i) {OutHover(positions[i]);})
	.style("font-family", "Courier")
	.style("text-anchor", "middle")
	.text(function(d) {return d;});

    // Draw each sample
    for (var i=0; i < samples.length; i++) {
	var currentHeight = 0;
	// Make div for the sample
	var samplesvg = d3.select("#"+samples[i]).append("svg:svg")
	    .attr("width",w)
	    .attr("height",(1+alignBySample[samples[i]].split(";").length)*gridHeight);
	// Draw reads
	sample_data = alignBySample[samples[i]];
	sample_data_reads = sample_data.split(";");
	for (var j = 0; j < sample_data_reads.length; j++) {
	    readdata = sample_data_reads[j].slice(fromindex, toindex+1).split("");
	    var SampleTrack = samplesvg.selectAll("gsamp_"+samples[i])
		.data(readdata)
		.enter().append("g");
	    SampleTrack.append("rect")
		.attr("x", function(d, pos) { return pos*gridWidth; })
		.attr("y", currentHeight)
		.attr("width", gridWidth)
		.attr("height", gridHeight)
		.attr("class", function(d, i) {return "p"+positions[i];})
		.style("fill", function(d, pos) {return (d.toUpperCase()!=refdata[pos].toUpperCase() &&
							 IsNuc(refdata[pos].toUpperCase()) && 
							 IsNuc(d.toUpperCase()))?"yellow":"white";});
	    SampleTrack.append("text")
		.text(function(d) {return d;})
		.attr("x", function(d, pos) {return pos*gridWidth+gridWidth/2;})
		.attr("y", currentHeight + gridHeight/2)
		.attr("dy", ".25em")
		.on("mouseover", function(d,i) {InHover(positions[i]);})
		.on("mouseout", function(d,i) {OutHover(positions[i]);})
		.style("font-family", "Courier")
		.style("text-anchor", "middle")
		.attr("fill", function(d) {return colors[d];});
	    currentHeight += gridHeight;
	}
	// Update position
	currentHeight += gridHeight*1.5;
    }
}

function toggleDiv(divname) {
    d = document.getElementById(divname);
    if (d.style.display != "none") {
	d.style.display = "none";
    } else {
	d.style.display = "block";
    }
}

// Scroll the sample div
var leftOffset = parseInt($("#sample").css('left')); //Grab the left position left first
$(window).scroll(function(){
	$('#sample').css({
	     'left': $(this).scrollLeft() + leftOffset //Use it later
    });
});

// Perform when the page loads
$(document).ready(function()
{

// Draw alignments
var frompos = parseInt(region.split("-")[0]);
var topos = parseInt(region.split("-")[1]);
fromindex=frompos-startpos;
toindex=topos-startpos;
DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex);

var w = 15; // TODO these are hard coded, change that
$("#aln").scrollLeft(w*250);
});