function toggleDiv(divname) {
    d = document.getElementById(divname);
    if (d.style.display != "none") {
	d.style.display = "none";
    } else {
	d.style.display = "block";
    }
}

function ScrollLeft() {
    // If scrolling left goes out of bounds, do nothing
    if (currentpos == minpos) {
	return;
    }
    // Set currentpos - 1 to visible
    var elemsleft = document.getElementsByClassName(chrom + "_" + (currentpos-1));
    for (var i = 0; i < elemsleft.length; i++) {
	elemsleft[i].style.display = "block";
    }
    // Set currentpos + NUMCHAR to invisible
    var elemsright = document.getElementsByClassName(chrom + "_" + (currentpos + NUMCHARS));
    for (var i = 0; i < elemsright.length; i++) {
	elemsright[i].style.display = "none";
    }
    // set currentpos to currentpos - 1
    currentpos = currentpos - 1;
}

function ScrollRight() {
    // If scrolling right goes out of bounds, do nothing
    if (currentpos == maxpos) {
	return;
    }
    // Set currentpos to invisible
    var elemsleft = document.getElementsByClassName(chrom + "_" + (currentpos));
    for (var i = 0; i < elemsleft.length; i++) {
	elemsleft[i].style.display = "none";
    }
    // Set currentpos + NUMCHAR + 1 to visible
    var elemsright = document.getElementsByClassName(chrom + "_" + (currentpos + NUMCHARS + 1));
    for (var i = 0; i < elemsright.length; i++) {
	elemsright[i].style.display = "block";
    }
    // Set currentpos to currentpos + 1
    currentpos = currentpos + 1;
}

$(document).keydown(function(e){
    // Scroll left (left arrow)
    if (e.keyCode == 37) { 
	ScrollLeft();
	return true;
    }
    // Scroll right (right arrow)
    if (e.keyCode == 39) {
	ScrollRight();
	return true;
    }
    // Big scroll left (r)
    if (e.keyCode == 82) {
	for (var i = 0; i < 10; i++) {
	    ScrollLeft();
	}
	return true;
    }
    // Big scroll right (a)
    if (e.keyCode == 65) {
	for (var i = 0; i < 10; i++) {
	    ScrollRight();
	}
	return true;
    }
});

// Get the width of the page to know how many bp to display
function SetPageWidth() {
    var width = $("#header_wrap").width();
    var form = document.forms[0];
    form.elements["width"].value = width;
    return true;
}

function UpdateTable() {
    // Set all table elements to none
    for (var i = currentpos - NUMCHARS; i < currentpos + NUMCHARS*2; i++) {
	elems = document.getElementsByClassName(chrom + "_" + i);
	for (var j = 0; j < elems.length; j++) {
	    elems[j].style.display = "none";
	}	
    }
    // Set the right ones to visible
    var form = document.forms[0];
    for (var i = currentpos; i < currentpos + (form.elements["width"].value/14); i++) {
	elems = document.getElementsByClassName(chrom + "_" + i);
	for (var j = 0; j < elems.length; j++) {
	    elems[j].style.display = "block";
	}
    }
}

$(window).resize(function()
{
    SetPageWidth();
    UpdateTable();
});
// Select columns by colgroup
$(document).ready(function()
{
    SetPageWidth();
$("td, th").hover
    (
     // mouseover
     function()
     {
	 cellClassName = $(this).attr("class");
	 $("." + cellClassName).addClass("hover");
	 var x=document.getElementById("selected");
	 x.innerHTML = "Selected: " + cellClassName.replace("_",":");
     },
     // mouseout
     function()
     {
	 $("." + cellClassName).removeClass("hover");
	 var x=document.getElementById("selected");
	 x.innerHTML = "Selected: ";
     }
     );
});