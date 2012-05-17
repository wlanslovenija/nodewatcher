/*
 * Mitar <mitar@tnode.com>
 * http://mitar.tnode.com/
 * In kind public domain.
 *
 * $Id: jquery.hashchange.js 110 2009-11-06 20:23:46Z mitar $
 * $Revision: 110 $
 * $HeadURL: https://common.tnode.com/svn/mitar/hashchange/trunk/src/jquery.hashchange.js $
*/

(function ($) {		
	var currentHash = null;

	$.fn.hashchange = function (f) {
		$(window).bind("jQuery.hashchange", f);
		if (currentHash == null) {
			init();
		}
		return this;
	};
	
	$.fn.updatehash = function (newhash) {
		triggerHash(newhash);
		document.location.hash = "#" + newhash; // Should be last as execution of a function can halt here
		return this;
	}
	
	function isOnhashchangeSupported() {
		if (typeof window.onhashchange != "undefined") {
			if (document.documentMode && (document.documentMode < 8)) {
				// IE does not fire event in compatibility mode but it does define it
				return false;
			}
			return true;
		}
		else {
			return false;
		}
	}
	
	function triggerHash(newHash) {
		if ((currentHash == null) || (currentHash != newHash)) {
			var oldHash = currentHash;
			currentHash = newHash;
			$(window).trigger("jQuery.hashchange", {"currentHash": currentHash, "oldHash": oldHash});
		}
	}
	
	function callTriggerHash() {
		triggerHash(document.location.hash.replace(/^#/, ''));
	}
	
	function init() {
		if (isOnhashchangeSupported()) {
			window.onhashchange = callTriggerHash;
		}
		else {
			setInterval(callTriggerHash, 200);
		}
		callTriggerHash();
	}
})(jQuery);
