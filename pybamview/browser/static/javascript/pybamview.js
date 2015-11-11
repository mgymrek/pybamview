BASE_W = 15;
BASE_H = 20;
BASE_FONT = 16;
REFCOLOR = "black";

function IsNuc(x) {
    return (x=="A" || x=="C" || x=="G" || x=="T");
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function Noop() {
}

function InHover(i, usefont) {
    var nodes = d3.selectAll(".p"+i)[0];
    for (var j = 0; j < nodes.length; j++) {
	if (nodes[j].style.fill == "rgb(255, 255, 255)" || nodes[j].style.fill == "white") {
	    nodes[j].style.fill = "rgb(255, 192, 203)";
	    nodes[j].style["stroke-width"] = 1;
	    nodes[j].style.stroke = "rgb(255, 192, 203)";
	}
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected: <b>" + chrom + ":" + i + "</b>";
}

function OutHover(i, usefont) {
    var nodes = d3.selectAll(".p"+i)[0];
    for (var j = 0; j < nodes.length; j++) {
	if (nodes[j].style.fill == "rgb(255, 192, 203)" || nodes[j].style.fill == "pink") {
	    nodes[j].style.fill = "rgb(255, 255, 255)";
	    nodes[j].style["stroke-width"] = 1;
	    nodes[j].style.stroke = "rgb(255, 255, 255)";
	}
    }
    // Update selected box
    var x = document.getElementById("selected");
    x.innerHTML = "Selected ";
}

function AlignZoom(zoomlevel, center_index) {
    // Set zoom level
    zoomlevel = parseFloat(zoomlevel);
    if (zoomlevel < 0) {
	zoomlevel = -1/zoomlevel;
    }
    var fromindex = Math.round(center_index - (buffer/zoomlevel/2));
    var toindex = Math.round(center_index + (buffer/zoomlevel/2));
    if (fromindex < 0) {
	fromindex = 0;
	toindex = fromindex + buffer/zoomlevel -1;
    }
    if (toindex >= positions.length) {
	toindex = positions.length  - 1;
	fromindex = toindex - buffer/zoomlevel + 1;
    }
    $("#centerind")[0].value = parseInt((fromindex+toindex)/2);
    // Redraw
    DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, false);
    // Scroll (try to keep previously visible section in the center)
    var w = parseInt($(".sample").css("width"));
    var vis1 = w/(BASE_W*zoomlevel);
    var vis0 = w/(BASE_W);
    var numBpToScroll = (buffer/zoomlevel/2) - (vis1-vis0)/2;
    $("#aln").scrollLeft(Math.round(BASE_W*zoomlevel*numBpToScroll));
}

function DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, snapshot) {
    // Update which region is displayed
    if (!snapshot) {
	var disp = document.getElementById("displayed");
	disp.innerHTML = "Displayed: <b>" + chrom + ":" + positions[fromindex] + "-" + positions[toindex] + " (" + numberWithCommas((positions[toindex]-positions[fromindex]+1)) + " bp)" + "</b>";
    }
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
    drawnucs = true;
    gridWidth = BASE_W*zoomlevel;
    gridHeight = BASE_H*zoomlevel;
    fontSize = BASE_FONT*zoomlevel;
    if (fontSize < 10) {
	fontSize = 10;
    }
    if (gridHeight < 10) {
	gridHeight = 10;
    }
    if (zoomlevel <= 1/3) {
	usefont = false;
	drawnucs = false;
    }
    var numreads = 0;
    for (var i=0; i < samples.length; i++) {
	var reads = alignBySample[samples[i]].split(";");
	for (var j=0; j<reads.length; j++) {
	    var read = reads[j].slice(fromindex, toindex+1);
	    if (reads[j].match(/-/g) == null) {numreads = numreads + 1;}
	    else if (reads[j].match(/-/g).length < reads[j].length) {
		numreads = numreads + 1;
	    }
	}
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
    if (drawnucs) {
	var RefTrack = refsvg.selectAll("gref")
	    .data(refdata)
	    .enter().append("g");
	RefTrack.append("rect")
	    .attr("x", function(d, i) { return i*gridWidth; })
	    .attr("y", function(d) {return usefont?0:(d.toUpperCase() == "."?gridHeight/3:0);})
	    .attr("width", gridWidth)
	    .attr("height", function(d) {return usefont?gridHeight:(d.toUpperCase() == "."?gridHeight/3:gridHeight);})
	    .attr("id", function(d, i) {return "ref"+i+fromindex;})
	    .on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
	    .on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
	    .style("fill", function(d) {return colors[d];})
	    .style("stroke", function(d) {return usefont?"white":colors[d];});
    } else {
	refsvg.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("height", gridHeight)
	    .attr("width", gridWidth*(toindex-fromindex+1))
	    .attr("fill", REFCOLOR);
	for (var r = 0; r < refdata.length; r++) {
	    if (refdata[r] == ".") {
		refsvg.append("rect")
		    .attr("x", r*gridWidth)
		    .attr("y", 0)
		    .attr("height", gridHeight)
		    .attr("width", gridWidth)
		    .attr("fill", "white")
		    .attr("stroke", "white");
		refsvg.append("rect")
		    .attr("x", r*gridWidth)
		    .attr("y", gridHeight/3)
		    .attr("height", gridHeight/3)
		    .attr("width", gridWidth)
		    .attr("fill", colors["."])
		    .attr("stroke", colors["."]);
	    }
	}
    }
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
    if (! snapshot) {
	function brush() {
	    var extent = refbrush.extent();
	    var startpos = positions[fromindex+Math.floor(extent[0]/gridWidth)];
	    var endpos = positions[fromindex+Math.ceil(extent[1]/gridWidth)];
	    var sel = document.getElementById("selected");
	    sel.innerHTML = "Selected: <b>" + chrom + ":" + startpos + "-" + endpos + "</b>";
	    d3.selectAll(".samplerect")
		.attr("x", extent[0])
		.attr("width", extent[1]-extent[0]);
	}
	function brushed() {
	    var extent0 = refbrush.extent(),
		extent1;
	    extent1 = [Math.floor(extent0[0]/gridWidth)*gridWidth, Math.ceil(extent0[1]/gridWidth)*gridWidth];
	    if (extent1[1]-extent1[0]<gridWidth*100) {
		var center = Math.round((extent1[1]+extent1[0])/2);
		extent1[0] = center-50;
		extent1[1] = center+50;
	    } // make region be at least 100bp
	    d3.select(this).call(refbrush.extent(extent1));
	    d3.selectAll(".samplerect")
		.attr("x", extent1[0])
		.attr("width", extent1[1]-extent1[0]);
	    if (extent1[1] > extent1[0]) {
		// Reset zoom and scroll to that region
		var find = fromindex+extent1[0]/gridWidth;
		var tind = fromindex+extent1[1]/gridWidth;
		var center_index = Math.round((find+tind)/2);
		var startpos = positions[find];
		var endpos = positions[tind];
		// Set zoom level
		var z = parseInt((endpos-startpos)/100);
		if (z < 1) {z = 1;}
		$("#centerind")[0].value = center_index;
		if (z != 1) {z = -1*z;}
		refreshZoom(z, center_index);
	    }
	    var sel = document.getElementById("selected");
	    sel.innerHTML = "Selected:";
	}
	var x = d3.scale.linear()
	    .domain([0,w])
	    .range([0,w]);
	var refbrush = d3.svg.brush()
	    .x(x)
	    .on("brush", brush)
	    .on("brushend", brushed);
	var gBrush = refsvg.append("g")
	    .attr("class","brush")
	    .call(refbrush);
	gBrush.selectAll("rect")
	    .attr("y", 0)
	    .attr("height", gridHeight*2);
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
		.style("font-size", fontSize)
		.style("stroke-width", "3px");
	    currentHeight += fontSize*1.1;
	} else {
	    var currentHeight = 23; // account for 22px sample div
	    // Make div for the sample
	    var numreads = 0;
	    var reads = alignBySample[samples[i]].split(";");
	    for (var k = 0; k<reads.length; k++) {
		var read = reads[k].slice(fromindex, toindex+1);
		if (read.match(/-/g) == null) { numreads = numreads + 1;}
		else if (read.match(/-/g).length < read.length) {
		    numreads = numreads + 1;
		}
	    }
	    var samplesvg = d3.select("#s"+samples[i]).append("svg:svg")
		.attr("width",w)
		.attr("height",(2+numreads)*gridHeight);
	}
	// Draw reads
	sample_data = alignBySample[samples[i]];
	sample_data_reads = sample_data.split(";");
	for (var j = 0; j < sample_data_reads.length; j++) {
	    readdata = sample_data_reads[j].slice(fromindex, toindex+1);
	    if (readdata.match(/-/g) != null) {if (readdata.match(/-/g).length == readdata.length) {continue;}}
	    readdata = readdata.split("");
	    if (drawnucs) {
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
	    } else {
		var read_start = 0;
		var read_end = 0;
		while (true) {
		    if (read_start >= readdata.length-1) {break;}
		    while (readdata[read_start] == "-") {
			read_start = read_start + 1;
			if (read_start >= readdata.length - 1) {
			    break;
			}
		    }
		    if (read_start >= readdata.length-1) {break;}
		    read_end = read_start+1;
		    while (readdata[read_end] != "-") {
			read_end = read_end + 1;
			if (read_end >= readdata.length -1) {
			    break;
			}
		    }
		    if (read_end > read_start) {
			samplesvg.append("rect")
			    .attr("x", read_start*gridWidth)
			    .attr("y", currentHeight)
			    .attr("width", (read_end - read_start + 1)*gridWidth)
			    .attr("height", gridHeight)
			    .attr("fill", "#F7F8E0")
			    .attr("stroke", "gray");
		    }
		    read_start = read_end+1;
		}
		for (var r=0; r < readdata.length; r++) {
		    if (readdata[r] == "." || readdata[r] == "*") {
			samplesvg.append("rect")
			    .attr("x", r*gridWidth)
			    .attr("y", currentHeight)
			    .attr("height", gridHeight)
			    .attr("width", gridWidth)
			    .attr("fill", "white")
			    .attr("stroke", "white");
			samplesvg.append("rect")
			    .attr("x", r*gridWidth)
			    .attr("y", gridHeight/3+currentHeight)
			    .attr("height", gridHeight/3)
			    .attr("width", gridWidth)
			    .attr("fill", colors["."])
			    .attr("stroke", colors["."]);
		    } else if (readdata[r].toUpperCase() != refdata[r].toUpperCase() &&
			       IsNuc(refdata[r].toUpperCase()) &&
			       IsNuc(readdata[r].toUpperCase())) {
			samplesvg.append("rect")
			    .attr("x", r*gridWidth)
			    .attr("y", currentHeight)
			    .attr("height", gridHeight)
			    .attr("width", gridWidth)
			    .attr("fill", colors[readdata[r]])
			    .attr("stroke", colors[readdata[r]]);
		    }
		}
	    }
	    if (usefont) {
		SampleTrack.append("text")
		    .text(function(d) {return d;})
		    .attr("x", function(d, pos) {return pos*gridWidth+gridWidth/2;})
		    .attr("y", currentHeight + gridHeight/2)
		    .attr("dy", ".25em")
		    .on("mouseover", function(d,i) {snapshot?Noop():InHover(positions[i+fromindex], usefont);})
		    .on("mouseout", function(d,i) {snapshot?Noop():OutHover(positions[i+fromindex], usefont);})
		    .style("font-family", "Courier")
		    .style("font-size", fontSize)
		    .style("text-anchor", "middle")
		    .attr("fill", function(d) {return colors[d];});
	    }
	    currentHeight += gridHeight;
	}
	var sampleBrushRect = samplesvg.append("rect")
	    .attr("class","samplerect")
	    .attr("fill-opacity", 0.5)
	    .attr("fill","pink")
	    .attr("stroke", "#fff")
	    .attr("height", (2+alignBySample[samples[i]].split(";").length)*gridHeight)
	    .attr("width", 0);
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

function scroll(direction) {
    var zoomlevel = parseInt(document.forms["controlform"]["zoomlevel"].value);
    if (zoomlevel < 1) {
      zoomlevel = -1/zoomlevel;
    }

    var magantude;
    if (Math.abs(direction) == 10) {
      magnatude = 10 // base pairs
    } else if (Math.abs(direction) == 100) {
      magnatude = 100 // base pairs
    } else {
      magnatude = buffer/zoomlevel/2 // default
    }

    var startpos;
    if (direction < 0) { // scroll left
      startpos = targetpos - magnatude;
    } else { // scroll right
      startpos = targetpos + magnatude;
    }

    document.forms["controlform"]["region"].value = chrom + ":" + startpos;
    document.forms["controlform"].submit();
}

function refreshZoom(zoom, center_index) {
    if ($("#centerind")[0].value != "") {center_index = parseInt($("#centerind")[0].value);}
    if (typeof center_index == "undefined") {center_index = parseInt(positions.length/2);}
    if (zoom < -60) {
	zoom = -100;
    } else if (zoom < -30) {
	zoom = -50;
    } else if (zoom < -10) {
	zoom = -10;
    }
    if ($("#zoom"+zoom).length == 0) {
	zoom = 1;
    }
    $("#zoomvalue").html("Zoom: <input type='text' maxlength='4' size='4' value='" + zoom + "x" + "' readonly>");
    document.forms["snapform"]["zoomlevel"].value = zoom;
    document.forms["controlform"]["zoomlevel"].value = zoom;
    $(".zoomout").css("background-color", "white");
    $(".zoomin").css("background-color", "white");
    $(".defaultzoom").css("background-color","gray");
    $("#zoom"+zoom).css("background-color", "black");
    AlignZoom(zoom, center_index);
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
	$(".sample").css({"width": w-2});
	var zoomlevel = parseFloat(document.forms["controlform"]["zoomlevel"].value);
	refreshZoom(zoomlevel, parseInt(positions.length/2));
	$("#helptextzoom").mouseover(function() {
		$(this).children("#descriptionzoom").show();
	    }).mouseout(function() {
		    $(this).children("#descriptionzoom").hide();
		});

	$("#helptextregion").mouseover(function() {
		$(this).children("#descriptionregion").show();
	    }).mouseout(function() {
		    $(this).children("#descriptionregion").hide();
		});

	$("#helptextselect").mouseover(function() {
		$(this).children("#descriptionselect").show();
	    }).mouseout(function() {
		    $(this).children("#descriptionselect").hide();
		});

	$("#helptextarrow").mouseover(function() {
		$(this).children("#descriptionarrow").show();
	    }).mouseout(function() {
		    $(this).children("#descriptionarrow").hide();
		});
    }
});
