var overrides = require('./src/overrides');

function injectScript(src) {
  var script = document.createElement('script');
  script.src = src;
  document.head.appendChild(script);
  return script;
}

function initWombatJS() {
  injectScript('/static/__pywb/wombat.js');
  
  function enableWombatJS() {
     if (window && window._WBWombat && !window._wb_js_inited && !window._wb_wombat) {
       window._wb_wombat = new window._WBWombat(wbinfo);
     }
  }
	var wombatInitScript = document.createElement('script');
	wombatInitScript.text = enableWombatJS.toString();
	document.head.appendChild(wombatInitScript);
}

if (window.wbinfo &&
    window.top.location.search.match(/\benable-wombat=1\b/)) {
  // enable the full rewriting of client side JS
  initWombatJS();
} else {
  if (window.wbinfo) {
    // the server-side part of pywb rewrites references to 'location'
    // with 'WB_wombat_location'. Add this for compatibility with
    // the mode where Wombat is enabled
    document.WB_wombat_location = document.location;
    window.WB_wombat_location = window.location;
    window.WB_wombat_top = window.top;
  }
  overrides.installOverrides();
}

