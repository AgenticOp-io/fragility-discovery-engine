/**
 * AgenticOps-branded nav/footer for Fragility Discovery Engine public site.
 * body[data-ao-page]: home | dashboard | whitepaper | cli
 */
(function () {
  var PAGE = document.body.getAttribute("data-ao-page") || "home";
  var AGENTICOP = "https://agenticop.io";

  var NAV_ITEMS = [
    ["home", "/", "Fragility"],
    ["dashboard", "/dashboard.html", "Dashboard"],
    ["whitepaper", "/whitepaper.html", "Whitepaper"],
    ["cli", "/cli.html", "CLI"],
  ];

  function navLinksHtml() {
    var parts = [];
    for (var i = 0; i < NAV_ITEMS.length; i++) {
      var id = NAV_ITEMS[i][0];
      var href = NAV_ITEMS[i][1];
      var label = NAV_ITEMS[i][2];
      var active = id === PAGE ? " ao-nav-link-active" : "";
      parts.push('<a class="ao-nav-link' + active + '" href="' + href + '">' + label + "</a>");
    }
    parts.push(
      '<a class="ao-nav-link" href="' +
        AGENTICOP +
        '" target="_blank" rel="noopener">agenticop.io</a>'
    );
    parts.push(
      '<a class="ao-nav-cta" href="https://github.com/AgenticOp-io/fragility-discovery-engine" target="_blank" rel="noopener">GitHub</a>'
    );
    return parts.join("");
  }

  function headerHtml() {
    return (
      '<div class="ao-wrap ao-nav-inner">' +
      '<a class="ao-brand" href="/" aria-label="Fragility Discovery Engine">' +
      '<img class="ao-brand-mark" src="/logo.svg" alt="" width="56" height="56" loading="eager" />' +
      '<span class="ao-brand-stack">' +
      '<span class="ao-brand-name">AgenticOps</span>' +
      '<span class="ao-brand-domain">Fragility Engine</span>' +
      "</span></a>" +
      '<nav class="ao-nav-links" aria-label="Primary">' +
      navLinksHtml() +
      "</nav></div>"
    );
  }

  function footerHtml() {
    var year = new Date().getFullYear();
    return (
      '<div class="ao-wrap ao-footer-inner">' +
      '<div class="ao-footer-brand">' +
      '<img class="ao-footer-mark" src="/logo.svg" alt="" width="48" height="48" loading="lazy" />' +
      '<span class="ao-brand-stack">' +
      '<span class="ao-brand-name ao-brand-name--footer">AgenticOps</span>' +
      '<span class="ao-brand-domain">Fragility Discovery Engine</span>' +
      "</span></div>" +
      '<nav class="ao-footer-links" aria-label="Footer">' +
      '<a href="/">Home</a>' +
      '<a href="/dashboard.html">Dashboard</a>' +
      '<a href="/whitepaper.html">Whitepaper</a>' +
      '<a href="/cli.html">CLI</a>' +
      '<a href="' +
      AGENTICOP +
      '">agenticop.io</a>' +
      '<a href="https://github.com/AgenticOp-io/fragility-discovery-engine" target="_blank" rel="noopener">Source</a>' +
      '<a href="https://github.com/AgenticOp-io/fragility-discovery-engine/issues/6">Feedback</a>' +
      "</nav>" +
      '<p class="ao-footer-fine">© <span id="ao-year">' +
      year +
      "</span> AgenticOps · Open-source fragility benchmarks · v0.5.0</p>" +
      "</div>"
    );
  }

  function inject() {
    var navEl = document.getElementById("ao-site-nav");
    var footEl = document.getElementById("ao-site-footer");
    if (navEl) navEl.innerHTML = headerHtml();
    if (footEl) footEl.innerHTML = footerHtml();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
