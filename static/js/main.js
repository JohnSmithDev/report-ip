function showHelp(ev) {
	var clickedThing = ev.target;
	var explanationEl = clickedThing.parentNode.nextElementSibling;
	var explClasses = explanationEl.getAttribute("class");

	if (explClasses.search( /hidden/i ) >= 0) {
		explanationEl.setAttribute("class", 
		                           explClasses.replace( /hidden/ig , ""));
	} else {
		explanationEl.setAttribute("class", 
		                           explClasses + " hidden");
	}
	ev.preventDefault();
}


var explainLinks = document.querySelectorAll(".explain-link");

for (var i=0; i<explainLinks.length; i++) {
	explainLinks[i].addEventListener("click",
	                                 showHelp,
	                                 false;
}

