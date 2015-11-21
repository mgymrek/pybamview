// get command line args
var paramfile = process.argv[2];

// load parameters
var params = require(paramfile);

// load pybamview library
var pbv = require(params.jspath + "alignments.js")

// load jsdom
var jsdom = require('jsdom');

// html stub
var htmlStub = '<html><head></head><body><div id="snapshot"></div></body></html>';

jsdom.env({
	features : { QuerySelector : true }
	, html : htmlStub
	, done : function(errors, window) {
		var el = window.document.querySelector('#snapshot');
		var body = window.document.querySelector("body");
		pbv.DrawSnapshot(params.reference_track, params.samples, params.alignBySample, params.fromindex, params.toindex, 1, true, el);
		if (params.filetype == "html") {
			console.log(body.innerHTML);
		} else if (params.filetype == "svg") {
			console.log(el.innerHTML);
		} else {
			console.log("Invalid file type");
		}
	}
})
