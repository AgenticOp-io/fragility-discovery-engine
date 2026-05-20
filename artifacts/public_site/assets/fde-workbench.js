/** Load GCE server status (benchmark validate, git head) — browser-only, same origin. */
(function () {
  var el = document.getElementById("fde-status");
  if (!el) return;
  fetch("/status.json", { cache: "no-store" })
    .then(function (r) {
      return r.json();
    })
    .then(function (s) {
      var ok = s.benchmark_validate === "ok";
      var cls = ok ? "fde-status-ok" : "fde-status-warn";
      el.innerHTML =
        '<span class="' +
        cls +
        '">Server · ' +
        (s.release || "?") +
        " · git " +
        (s.git_head || "?") +
        " · benchmarks " +
        (s.benchmark_validate || "?") +
        "</span> · updated " +
        (s.checked_utc || "?");
    })
    .catch(function () {
      el.textContent = "Server status unavailable";
    });
})();
