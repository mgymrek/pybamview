BASE_W = 15;
BASE_H = 20;
BASE_FONT = 16;

function IsNuc(x) {
    return (x=="A" || x=="C" || x=="G" || x=="T");
}

function InHover(i, usefont) {
    if (usefont) {
	// Update color
	d3.selectAll(".p"+i).style("fill","pink");
    } else {
	d3.selectAll(".p"+i)
	    .style("stroke","black")
	    .style("stroke-width",1);
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected: " + chrom + ":" + i;
}

function OutHover(i, usefont) {
    if (usefont) {
	// Update color
	d3.selectAll(".p"+i).style("fill","white");
    } else {
	d3.selectAll(".p"+i).style("stroke-width",0);
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected ";
}

function AlignZoom(zoomlevel) {
    var frompos = parseInt(region.split("-")[0]);
    var topos = parseInt(region.split("-")[1]);
    fromindex=frompos-startpos;
    toindex=topos-startpos;
    zoomlevel = parseFloat(zoomlevel);
    if (zoomlevel < 0) {
	zoomlevel = -1/zoomlevel;
    }
    DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel);
    // TODO - scroll, don't make hardcoded
    $("#aln").scrollLeft(BASE_W*zoomlevel*250);
}

function DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel) {
    // Reset
    document.getElementById("reference").innerHTML = "";
    var divs = document.getElementsByClassName("sampleAlignment");
    for (var i = 0; i<divs.length; i++) {
	divs[i].innerHTML = "";
    }
    // Set positioning variables
    usefont = true;
    gridWidth = BASE_W*zoomlevel;
    gridHeight = BASE_H*zoomlevel;
    fontSize = BASE_FONT*zoomlevel;
    if (gridHeight < 10) {
	gridHeight = 10;
    }
    if (zoomlevel < 1/3) {
	usefont = false;
    }
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
	.on("mouseover", function(d,i) {InHover(positions[i], usefont);})
	.on("mouseout", function(d,i) {OutHover(positions[i], usefont);})
	.style("fill", function(d) {return colors[d];})
	.style("stroke", function(d) {return usefont?"white":colors[d];});
    if (usefont) {
	RefTrack.append("text")
	    .attr("x", function(d, i) {return i*gridWidth+gridWidth/2; })
	    .attr("y", gridHeight/2)
	    .attr("dy", ".25em")
	    .attr("fill", "white")
	    .on("mouseover", function(d,i) {InHover(positions[i], usefont);})
	    .on("mouseout", function(d,i) {OutHover(positions[i], usefont);})
	    .style("font-family", "Courier")
	    .style("font-size", fontSize)
	    .style("text-anchor", "middle")
	    .text(function(d) {return d;});
    }
    // Draw each sample
    for (var i=0; i < samples.length; i++) {
	var currentHeight = 20;
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
		.on("mouseover", function(d,i) {InHover(positions[i], usefont);})
		.on("mouseout", function(d,i) {OutHover(positions[i], usefont);})
		.style("fill", function(d, pos) {return (d.toUpperCase()!=refdata[pos].toUpperCase() &&
							 IsNuc(refdata[pos].toUpperCase()) && 
							 IsNuc(d.toUpperCase()))?"yellow":(usefont?"white":colors[d]);});
	    if (usefont) {
		SampleTrack.append("text")
		    .text(function(d) {return d;})
		    .attr("x", function(d, pos) {return pos*gridWidth+gridWidth/2;})
		    .attr("y", currentHeight + gridHeight/2)
		    .on("mouseover", function(d,i) {InHover(positions[i], usefont);})
		    .on("mouseout", function(d,i) {OutHover(positions[i], usefont);})
		    .style("font-family", "Courier")
		    .style("font-size", fontSize)
		    .style("text-anchor", "middle")
		    .attr("fill", function(d) {return colors[d];});
	    }
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
DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, 1);

// TODO these are hard coded, change that
$("#aln").scrollLeft(BASE_W*250);
});