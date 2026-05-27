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

/** Guided tour overlay (manual + autoplay). */
(function () {
  var TOUR_ACTIVE = "fde_tour_active_v1";
  var TOUR_INDEX = "fde_tour_index_v1";
  var TOUR_AUTOPLAY = "fde_tour_autoplay_v1";
  var TOUR_MS = "fde_tour_ms_v1";
  var TOUR_PLAYING = "fde_tour_playing_v1";

  function qs(sel) {
    try { return document.querySelector(sel); } catch (e) { return null; }
  }
  function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
  function pagePath() { return (window.location.pathname || "/") + (window.location.hash || ""); }
  function setText(el, txt) { if (el) el.textContent = String(txt || ""); }

  var steps = [
    {
      url: "/",
      selector: ".fde-hero-actions a[href=\"/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json\"]",
      title: "1) Watch a collapse",
      body: "Open the flagship replay. Then step the timeline to see exactly when the system crosses its breaking point.",
    },
    {
      url: "/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json",
      selector: "canvas",
      title: "Replay timeline",
      body: "Drag or click on the chart to scrub through time. Look for the collapse marker and the instability curve.",
    },
    {
      url: "/run.html",
      selector: "#runBtn",
      title: "2) Run a live search",
      body: "Keep the defaults and press Run scenario. The server will search for a worst‑case schedule and open the results.",
    },
    {
      url: "/artifacts/attribution_viewer/index.html#src=sample_aggregate_chain_rumor_depeg.json",
      selector: "#presetSelect",
      title: "3) Ask “what caused it?”",
      body: "This view shows a mutation chain: each step adds one change and shows its Δ instability and Δ cost.",
    },
    {
      url: "/artifacts/composite_viewer/index.html#src=../composite_demo/sample_hexa_composite.json",
      selector: "select, .btn, button",
      title: "Bonus: compare all six domains",
      body: "The composite view applies the same attack to every domain side‑by‑side. Try presets to switch bundles.",
    },
  ];

  function currentIndex() {
    var raw = parseInt(sessionStorage.getItem(TOUR_INDEX) || "0", 10);
    if (!isFinite(raw)) raw = 0;
    return clamp(raw, 0, steps.length - 1);
  }
  function setIndex(i) { sessionStorage.setItem(TOUR_INDEX, String(clamp(i, 0, steps.length - 1))); }
  function setPlaying(v) { sessionStorage.setItem(TOUR_PLAYING, v ? "1" : "0"); }
  function isPlaying() {
    if (sessionStorage.getItem(TOUR_AUTOPLAY) !== "1") return false;
    var raw = sessionStorage.getItem(TOUR_PLAYING);
    if (raw == null) return true;
    return raw === "1";
  }

  function isTourActive() {
    var urlFlag = (new URLSearchParams(window.location.search)).get("tour");
    return urlFlag === "1" || sessionStorage.getItem(TOUR_ACTIVE) === "1";
  }

  function ensureTourStartedFromUrl() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("tour") !== "1") return;
    sessionStorage.setItem(TOUR_ACTIVE, "1");
    var ap = params.get("autoplay");
    if (ap === "1") {
      sessionStorage.setItem(TOUR_AUTOPLAY, "1");
      setPlaying(true);
    }
    var ms = parseInt(params.get("ms") || "", 10);
    if (isFinite(ms) && ms >= 1500) sessionStorage.setItem(TOUR_MS, String(ms));
    params.delete("tour"); params.delete("autoplay"); params.delete("ms");
    var qs2 = params.toString();
    history.replaceState(null, "", window.location.pathname + (qs2 ? "?" + qs2 : "") + window.location.hash);
  }

  function teardown() {
    var root = document.getElementById("fdeTourRoot");
    if (root && root.parentNode) root.parentNode.removeChild(root);
  }

  function exitTour() {
    sessionStorage.removeItem(TOUR_ACTIVE);
    sessionStorage.removeItem(TOUR_INDEX);
    sessionStorage.removeItem(TOUR_AUTOPLAY);
    sessionStorage.removeItem(TOUR_PLAYING);
    sessionStorage.removeItem(TOUR_MS);
    teardown();
  }

  function ensureOnStep(i) {
    var step = steps[i];
    if (!step) return false;
    var here = pagePath();
    var want = step.url;
    if (here === want) return true;
    window.location.href = want + (want.indexOf("?") >= 0 ? "&" : "?") + "tour=1";
    return false;
  }

  function computeTargetRect(step) {
    if (!step || !step.selector) return null;
    var el = qs(step.selector);
    if (!el) return null;
    try { el.scrollIntoView({ block: "center", inline: "center" }); } catch (e) {}
    var r = el.getBoundingClientRect();
    if (!r || !isFinite(r.left) || !isFinite(r.top)) return null;
    var pad = 10;
    return {
      left: Math.max(6, r.left - pad),
      top: Math.max(6, r.top - pad),
      width: Math.max(24, r.width + pad * 2),
      height: Math.max(24, r.height + pad * 2),
    };
  }

  function render() {
    teardown();
    var i = currentIndex();
    if (!ensureOnStep(i)) return;
    var step = steps[i];

    var root = document.createElement("div");
    root.id = "fdeTourRoot";
    root.innerHTML = [
      '<div class="fde-tour-dim"></div>',
      '<div class="fde-tour-spot" aria-hidden="true"></div>',
      '<div class="fde-tour-card" role="dialog" aria-label="Guided tour">',
      '  <div class="fde-tour-kicker">Tour</div>',
      '  <div class="fde-tour-title" id="fdeTourTitle"></div>',
      '  <div class="fde-tour-body" id="fdeTourBody"></div>',
      '  <div class="fde-tour-caption" id="fdeTourCaption"></div>',
      '  <div class="fde-tour-progress-wrap"><div class="fde-tour-progress-bar" id="fdeTourBar"></div></div>',
      '  <div class="fde-tour-controls">',
      '    <button type="button" class="fde-tour-btn" id="fdeTourBack">Back</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-primary" id="fdeTourNext">Next</button>',
      '    <button type="button" class="fde-tour-btn" id="fdeTourPlay">Pause</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-ghost" id="fdeTourExit">Exit</button>',
      '  </div>',
      '  <div class="fde-tour-progress" id="fdeTourProgress"></div>',
      "</div>",
    ].join("");
    document.body.appendChild(root);

    setText(document.getElementById("fdeTourTitle"), step.title);
    setText(document.getElementById("fdeTourBody"), step.body);
    setText(document.getElementById("fdeTourCaption"), "Narration: " + step.body);
    setText(document.getElementById("fdeTourProgress"), (i + 1) + " / " + steps.length);

    var back = document.getElementById("fdeTourBack");
    var next = document.getElementById("fdeTourNext");
    var play = document.getElementById("fdeTourPlay");
    var exit = document.getElementById("fdeTourExit");
    if (back) back.disabled = i <= 0;
    if (next) next.textContent = (i >= steps.length - 1) ? "Finish" : "Next";
    if (play) {
      if (sessionStorage.getItem(TOUR_AUTOPLAY) === "1") {
        play.style.display = "";
        play.textContent = isPlaying() ? "Pause" : "Play";
      } else {
        play.style.display = "none";
      }
    }

    if (back) back.onclick = function () { setIndex(i - 1); render(); };
    if (next) next.onclick = function () {
      if (i >= steps.length - 1) { exitTour(); return; }
      setIndex(i + 1); render();
    };
    if (play) play.onclick = function () {
      setPlaying(!isPlaying());
      render();
    };
    if (exit) exit.onclick = function () { exitTour(); };

    function position() {
      var rect = computeTargetRect(step);
      var spot = root.querySelector(".fde-tour-spot");
      if (rect && spot) {
        spot.style.display = "block";
        spot.style.left = rect.left + "px";
        spot.style.top = rect.top + "px";
        spot.style.width = rect.width + "px";
        spot.style.height = rect.height + "px";
      } else if (spot) {
        spot.style.display = "none";
      }
    }
    position();
    window.addEventListener("resize", position, { passive: true });
    window.addEventListener("scroll", position, { passive: true });

    var autoplay = sessionStorage.getItem(TOUR_AUTOPLAY) === "1";
    if (autoplay) {
      var ms = parseInt(sessionStorage.getItem(TOUR_MS) || "5200", 10);
      if (!isFinite(ms)) ms = 5200;
      ms = clamp(ms, 2000, 12000);
      var bar = document.getElementById("fdeTourBar");
      if (bar) {
        bar.style.transition = "none";
        bar.style.width = "0%";
        if (isPlaying()) {
          window.requestAnimationFrame(function () {
            bar.style.transition = "width " + ms + "ms linear";
            bar.style.width = "100%";
          });
        }
      }
      if (!isPlaying()) return;
      window.setTimeout(function () {
        // Don't auto-advance if user already navigated away or closed.
        if (!document.getElementById("fdeTourRoot")) return;
        if (currentIndex() !== i) return;
        if (!isPlaying()) return;
        if (i >= steps.length - 1) { exitTour(); return; }
        setIndex(i + 1);
        render();
      }, ms);
    }
  }

  ensureTourStartedFromUrl();
  if (!isTourActive()) return;
  // Default to step 0 when activated without index.
  if (!sessionStorage.getItem(TOUR_INDEX)) sessionStorage.setItem(TOUR_INDEX, "0");
  render();
})();
