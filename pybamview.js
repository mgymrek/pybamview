function toggleDiv(divname) {
    d = document.getElementById(divname);
    if (d.style.display != "none") {
	d.style.display = "none";
    } else {
	d.style.display = "block";
    }
}

// Select columns by colgroup
$(document).ready(function()
{
var w = $("#ref0").outerWidth()+0.5;
$("#aln").scrollLeft(w*250);

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