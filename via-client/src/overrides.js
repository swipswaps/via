/**
 * Disables password fields to prevent the user
 * submitting authentication credentials into
 * sites served by the proxy.
 */
function disableFormFields(document) {
  // this is currently limited to password fields. We could opt
  // to be much more thorough and disable all inputs
  var fields = document.querySelectorAll('input[type="password"]');
  for (var i=0; i < fields.length; i++) {
    fields[i].disabled = true;
  }
}

/**
 * Overrides document.cookie to make it non-persistent.
 * Any cookies that are created or updated are 
 */
function disablePersistentCookies(document) {
  var cookies = {};

  function serializeCookies(cookies) {
    return Object.keys(cookies).map(function (name) {
      return name + '=' + cookies[name];
    }).join(';');
  }

  function parseCookie(cookieStr) {
    var parts = cookieStr.split(/=|;/);
    var name = parts[0] || '';
    var value = parts[1] || '';
    return {
      name: name,
      value: value
    };
  }

  Object.defineProperty(Object.getPrototypeOf(document), 'cookie', {
    get: function () {
      return serializeCookies(cookies);
    },

    set: function (cookieStr) {
      var cookie = parseCookie(cookieStr);
      cookies[cookie.name] = cookie.value;
      return cookieStr;
    }
  });
}

function installOverrides() {
  // disable some of the page features
  // which could cause private user data to be leaked
  // either to the proxy or between pages served by
  // different domains when using the proxy
  disablePersistentCookies(document);

  document.addEventListener('DOMContentLoaded', function () {
    disableFormFields(document);
  });
}

module.exports = {
  disableFormFields: disableFormFields,
  disablePersistentCookies: disablePersistentCookies,
  installOverrides: installOverrides
};

