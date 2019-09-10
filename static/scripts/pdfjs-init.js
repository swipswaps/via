'use strict';

// Note: This file is not transpiled. For IE 11 compatibility, it must only
// use ES5 language features.

// Listen for `webviewerloaded` event to configure the viewer after its files
// have been loaded but before it is initialized.
document.addEventListener('webviewerloaded', function(event) {
  var appOptions = window.PDFViewerApplicationOptions;

  // Read configuration rendered into template as global vars.
  var url = VIA_DOCUMENT_URL;
  var clientEmbedUrl = VIA_H_EMBED_URL;

  // Load the PDF specified in the URL.
  //
  // See https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions#can-i-specify-a-different-pdf-in-the-default-viewer and https://github.com/mozilla/pdf.js/issues/10435#issuecomment-452706770
  //
  // Prevent loading of the default PDF bundled with the viewer.
  appOptions.set('defaultUrl', '');
  var app = window.PDFViewerApplication;
  app.open({
    // Load PDF through Via to work around CORS restrictions.
    url: '/id_/' + url,

    // Make sure `PDFViewerApplication.url` returns the original URL, as this
    // is the URL associated with annotations.
    originalUrl: url,
  }).then(function () {
    // Once the PDF has been loaded, then inject the client.
    var embedScript = document.createElement('script');
    embedScript.src = clientEmbedUrl;
    document.body.appendChild(embedScript);
  });
});
