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

// Select columns by colgroup
$(document).ready(function()
{
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