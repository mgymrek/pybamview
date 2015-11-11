// get command line args
var paramfile = process.argv[2];

// load parameters
var params = require(paramfile); // TODO maybe include path to alignments.js here

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
		pbv.DrawSnapshot(params.reference_track, params.samples, params.alignBySample, params.fromindex, params.toindex, 1, true, el);
		console.log(el.innerHTML);
	}
})
