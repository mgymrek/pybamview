BASE_W = 15;
BASE_H = 20;
BASE_FONT = 16;
ZOOMDEFAULT = 82;

function IsNuc(x) {
    return (x=="A" || x=="C" || x=="G" || x=="T");
}

function Noop() {
}

function InHover(i, usefont) {
    if (usefont) {
	// Update color
	d3.selectAll(".p"+i).style("fill","pink");
    } else {
	var nodes = d3.selectAll(".p"+i)[0];
	for (var j = 0; j < nodes.length; j++) {
	    if (nodes[j].style.fill == "rgb(255, 255, 255)" || nodes[j].style.fill == "white") {
		nodes[j].style.fill = "rgb(255, 192, 203)";
		nodes[j].style["stroke-width"] = 1;
		nodes[j].style.stroke = "rgb(255, 192, 203)";
	    }
	}
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected: <b>" + chrom + ":" + i + "</b>";
}

function OutHover(i, usefont) {
    if (usefont) {
	// Update color
	d3.selectAll(".p"+i).style("fill","white");
    } else {
	var nodes = d3.selectAll(".p"+i)[0];
	for (var j = 0; j < nodes.length; j++) {
	    if (nodes[j].style.fill == "rgb(255, 192, 203)" || nodes[j].style.fill == "pink") {
		nodes[j].style.fill = "rgb(255, 255, 255)";
		nodes[j].style["stroke-width"] = 1;
		nodes[j].style.stroke = "rgb(255, 255, 255)";
	    }
	}
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected ";
}

function AlignZoom(zoomlevel) {
    // Set zoom level
    zoomlevel = parseFloat(zoomlevel);
    if (zoomlevel < 0) {
	zoomlevel = -1/zoomlevel;
    }
    var center_index = positions.length/2;
    var fromindex = Math.round(center_index - (buffer/zoomlevel/2));
    var toindex = Math.round(center_index + (buffer/zoomlevel/2));
    // Redraw
    DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, false);
    // Scroll (try to keep previously visible section in the center)
    var w = parseInt($("#sample").css("width"));
    var vis1 = w/(BASE_W*zoomlevel);
    var vis0 = w/(BASE_W);
    var numBpToScroll = (buffer/zoomlevel/2) - (vis1-vis0)/2;
    $("#aln").scrollLeft(Math.round(BASE_W*zoomlevel*numBpToScroll));
}

function DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, snapshot) {
    // Reset
    if (snapshot) {
	document.getElementById("snapshot").innerHTML = "";
    } else {
	document.getElementById("reference").innerHTML = "";
	var divs = document.getElementsByClassName("sampleAlignment");
	for (var i = 0; i<divs.length; i++) {
	    divs[i].innerHTML = "";
	}
    }
    // Set positioning variables
    usefont = true;
    gridWidth = BASE_W*zoomlevel;
    gridHeight = BASE_H*zoomlevel;
    fontSize = BASE_FONT*zoomlevel;
    if (gridHeight < 10) {
	gridHeight = 10;
    }
    if (zoomlevel < 1/2) {
	usefont = false;
    }
    var numreads = 0;
    for (var i=0; i < samples.length; i++) {
	numreads += alignBySample[samples[i]].split(";").length;
    }
    var w = gridWidth*(toindex-fromindex+1);
    var h = (samples.length*2+numreads)*gridHeight+BASE_H;

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
    if (snapshot) {
	var svg = d3.select("#snapshot").append("svg:svg")
	    .attr("width", w)
	    .attr("height", h);
	var refsvg = svg;
    } else {
	var refsvg = d3.select("#reference").append("svg:svg")
	    .attr("width", w)
	    .attr("height", gridHeight);
    }
    // Draw reference
    var refdata = reference_track.slice(fromindex, toindex+1).split("");
    var RefTrack = refsvg.selectAll("gref")
	.data(refdata)
	.enter().append("g");
    RefTrack.append("rect")
	.attr("x", function(d, i) { return i*gridWidth; })
	.attr("y", function(d) {return usefont?0:(d.toUpperCase() == "."?gridHeight/3:currentHeight);})
	.attr("width", gridWidth)
	.attr("height", function(d) {return usefont?gridHeight:(d.toUpperCase() == "."?gridHeight/3:gridHeight);})
	.attr("id", function(d, i) {return "ref"+i+fromindex;})
	.on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
	.on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
	.style("fill", function(d) {return colors[d];})
	.style("stroke", function(d) {return usefont?"white":colors[d];});
    if (usefont) {
	RefTrack.append("text")
	    .attr("x", function(d, i) {return i*gridWidth+gridWidth/2; })
	    .attr("y", gridHeight/2)
	    .attr("dy", ".25em")
	    .attr("fill", "white")
	    .on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
	    .on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
	    .style("font-family", "Courier")
	    .style("font-size", fontSize)
	    .style("text-anchor", "middle")
	    .text(function(d) {return d;});
    }
    // Draw each sample
    if (snapshot) { var currentHeight = gridHeight*1.6;}
    for (var i=0; i < samples.length; i++) {
	if (snapshot) {
	    samplesvg = svg;
	    // Append sample label
	    svg.append("text")
		.text(samples[i])
		.attr("x", 1)
		.attr("y", currentHeight+gridHeight/2)
		.attr("dy","0.25em")
		.attr("fill","black")
		.style("font-family", "Courier")
		.style("font-size", "16px;")
		.style("stroke-width", "3px");
	    currentHeight += BASE_H;
	} else {
	    var currentHeight = 20;
	    // Make div for the sample
	    var samplesvg = d3.select("#"+samples[i]).append("svg:svg")
		.attr("width",w)
		.attr("height",(1+alignBySample[samples[i]].split(";").length)*gridHeight);
	}
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
		.attr("y", function(d) {return usefont?currentHeight:(d.toUpperCase() == "."?currentHeight+gridHeight/3:currentHeight);})
		.attr("width", gridWidth)
		.attr("height", function(d) {return usefont?gridHeight:(d.toUpperCase() == "."?gridHeight/3:gridHeight);})
		.attr("class", function(d, i) {return snapshot?"":"p"+positions[i+fromindex];})
		.on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
		.on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
		.style("stroke-width", 0)
		.style("fill", function(d, pos) {return usefont?((d.toUpperCase()!=refdata[pos].toUpperCase() &&
							 IsNuc(refdata[pos].toUpperCase()) && 
								  IsNuc(d.toUpperCase()))?"yellow":"white"):colors[d];});
	    if (usefont) {
		SampleTrack.append("text")
		    .text(function(d) {return d;})
		    .attr("x", function(d, pos) {return pos*gridWidth+gridWidth/2;})
		    .attr("y", currentHeight + gridHeight/2)
		    .on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
		    .on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
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

function refreshZoom(zoom) {
    $("#zoomvalue").html("Zoom: " + zoom + "x");
    document.forms["snapform"]["zoomlevel"].value = zoom;
    document.forms["controlform"]["zoomlevel"].value = zoom;
    $(".zoomout").css("background-color", "white");
    $(".zoomin").css("background-color", "white");
    $(".defaultzoom").css("background-color","gray");
    $("#zoom"+zoom).css("background-color", "black");
    AlignZoom(zoom);
}

// Perform when the page loads
$(document).ready(function()
{
    if (snapshot) {
	// Draw default when load page
	var region = document.forms["snapform"]["region"].value;
	var frompos = parseInt(region.split("-")[0]);
	var topos = parseInt(region.split("-")[1]);
	var fromindex=frompos-startpos;
	var toindex=topos-startpos;
	var zoomlevel = parseFloat(document.forms["snapform"]["zoomlevel"].value);
	if (zoomlevel < 0) {
	    zoomlevel = -1/zoomlevel;
	}
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
		 DrawSnapshot(reference_track, samples_subset, alignBySample, fromindex, toindex, zoomlevel, true);
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
    } else {
	var w = parseInt($("#toolbar").css("width"));
	$(".sample").css({"width": w});
	var zoomlevel = parseFloat(document.forms["controlform"]["zoomlevel"].value);
	AlignZoom(zoomlevel);
	$(".zoomout, .zoomin, .defaultzoom").hover(
						   function() {
						       $(this).addClass("hover");
						   }, function() {
						       $(this).removeClass("hover");
						   }
						   );
    }
});