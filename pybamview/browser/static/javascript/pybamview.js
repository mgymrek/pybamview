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
	DrawSnapshot(reference_track, samples, alignBySample, fromindex, toindex, zoomlevel, true, undefined);
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
		 DrawSnapshot(reference_track, samples_subset, alignBySample, fromindex, toindex, zoomlevel, true, undefined);
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
