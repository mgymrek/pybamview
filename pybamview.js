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