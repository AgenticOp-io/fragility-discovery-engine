/** Load GCE server status (benchmark validate, git head) — browser-only, same origin. */
(function () {
  var el = document.getElementById("fde-status");
  if (!el) return;
  fetch("/status.json", { cache: "no-store" })
    .then(function (r) {
      return r.json();
    })
    .then(function (s) {
      var benchOk = s.benchmark_validate === "ok";
      var forkOk = s.research_fork_validate == null || s.research_fork_validate === "ok";
      var paretoOk = s.coupled_fork_pareto_v1 == null || s.coupled_fork_pareto_v1 === "ok";
      var hvOk = s.bundled_pareto_hypervolume == null || s.bundled_pareto_hypervolume === "ok";
      var ok = benchOk && forkOk && paretoOk && hvOk;
      var cls = ok ? "fde-status-ok" : "fde-status-warn";
      var forkBit =
        s.research_fork_validate != null
          ? " · coupled fork " + s.research_fork_validate
          : "";
      var ops = [];
      if (s.dns_ready === true) ops.push("DNS");
      else if (s.dns_ready === false) ops.push("DNS pending");
      if (s.pypi_ready === "ok") ops.push("PyPI ready");
      else if (s.pypi_ready === "failed") ops.push("PyPI check failed");
      if (s.coupled_fork_pareto_v1) ops.push("pareto pins " + s.coupled_fork_pareto_v1);
      if (s.bundled_pareto_hypervolume) ops.push("HV " + s.bundled_pareto_hypervolume);
      var opsBit = ops.length ? " · " + ops.join(" · ") : "";
      el.innerHTML =
        '<span class="' +
        cls +
        '">Server · ' +
        (s.release || "?") +
        " · git " +
        (s.git_head || "?") +
        " · benchmarks " +
        (s.benchmark_validate || "?") +
        forkBit +
        opsBit +
        "</span> · updated " +
        (s.checked_utc || "?");
    })
    .catch(function () {
      el.textContent = "Server status unavailable";
    });
})();

/** Guided tour overlay (manual step-by-step + optional autoplay). */
(function () {
  var TOUR_ACTIVE = "fde_tour_active_v1";
  var TOUR_INDEX = "fde_tour_index_v1";
  var TOUR_AUTOPLAY = "fde_tour_autoplay_v1";
  var TOUR_MS = "fde_tour_ms_v1";
  var TOUR_PLAYING = "fde_tour_playing_v1";
  var TOUR_REDIRECTS = "fde_tour_redirects_v1";
  var TOUR_NAV_TARGET = "fde_tour_nav_target_v1";
  var floatExitEl = null;
  var autoplayTimer = null;

  function qs(sel) {
    try { return document.querySelector(sel); } catch (e) { return null; }
  }
  function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
  function setText(el, txt) { if (el) el.textContent = String(txt || ""); }
  function setBodyHtml(el, txt) {
    if (!el) return;
    var parts = String(txt || "").split(/\n\n+/).filter(function (p) { return p.trim(); });
    if (!parts.length) {
      el.textContent = "";
      return;
    }
    el.innerHTML = parts
      .map(function (p) {
        return "<p>" + p.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") + "</p>";
      })
      .join("");
  }

  function normalizeHash(hash) {
    if (!hash) return "";
    var h = hash;
    h = h.replace(/\?tour=1(&|$)/, "$1").replace(/&tour=1/g, "");
    if (h === "#" || h === "#&") return "";
    return h;
  }

  function splitPath(url) {
    var path = url || "/";
    var hash = "";
    var hi = path.indexOf("#");
    if (hi >= 0) {
      hash = normalizeHash(path.slice(hi));
      path = path.slice(0, hi) || "/";
    }
    return { path: path, hash: hash };
  }

  function pagePath() {
    return (window.location.pathname || "/") + normalizeHash(window.location.hash || "");
  }

  function pathsMatch(want, here) {
    var w = splitPath(want);
    var h = splitPath(here);
    if (w.path !== h.path) return false;
    if (!w.hash) return true;
    if (w.hash === h.hash) return true;
    try {
      return decodeURIComponent(w.hash) === decodeURIComponent(h.hash);
    } catch (e) {
      return false;
    }
  }

  function isTourPage() {
    var p = window.location.pathname || "/";
    if (p === "/" || p === "/run.html" || p === "/tour.html") return true;
    return /\/artifacts\/[a-z_]+_viewer\/index\.html$/i.test(p);
  }

  function stripTourFromUrl() {
    var params = new URLSearchParams(window.location.search);
    var changed = params.has("tour") || params.has("autoplay") || params.has("ms");
    if (!changed) return;
    params.delete("tour");
    params.delete("autoplay");
    params.delete("ms");
    var qs = params.toString();
    history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : "") + normalizeHash(window.location.hash || ""));
  }

  function navigateToStepUrl(want) {
    var parts = want.split("#");
    var base = parts[0] || "/";
    var hash = parts.length > 1 ? "#" + parts.slice(1).join("#") : "";
    var sep = base.indexOf("?") >= 0 ? "&" : "?";
    window.location.assign(base + sep + "tour=1" + hash);
  }

  var steps = [
    {
      url: "/",
      selector: ".fde-hero-actions a[href=\"/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json\"]",
      title: "1) Watch a collapse",
      body:
        "This workbench hosts pre-built JSON samples on the server — nothing is uploaded from your computer.\n\n" +
        "Start with the flagship benchmark replay: a genetic search already found one of the worst stress schedules for the aggregate peg domain (stablecoin reserves under panic). Click the highlighted link to open it in the replay viewer.\n\n" +
        "In the viewer you will scrub a step-by-step timeline: reserve ratio, panic level, applied shocks, and a collapse marker when the system crosses its breaking point.",
      hint: "Click Flagship replay to open the timeline viewer.",
    },
    {
      url: "/artifacts/replay_viewer/index.html#src=sample_replay.json",
      selector: "canvas",
      title: "2) Read the replay chart",
      body:
        "The replay viewer turns a JSON file into an interactive timeline. The sample loaded here is a shorter aggregate-peg run.\n\n" +
        "Drag across the chart or click a step to move through time. Watch three things: the instability curve climbing toward failure, the event lane showing external shocks at each step, and the collapse marker (if the run ended in failure).\n\n" +
        "Every sample on this demo uses the Presets menu or workbench links — local file upload is disabled on the public site.",
      hint: "Scrub the chart (highlighted) to step through the simulation.",
    },
    {
      url: "/run.html",
      selector: "#runBtn",
      title: "3) Run a live search on the server",
      body:
        "So far you have browsed frozen samples. This page runs a new search on the GCE server.\n\n" +
        "Pick a domain and search type from the dropdown, set seed / horizon / generations / population, then press Run scenario. The engine runs a genetic algorithm, saves results under /runs/<id>/, and links you to the replay or Pareto viewer when finished.\n\n" +
        "For this step, keep the defaults (aggregate peg) and click Run scenario. You do not need to change any fields.",
      hint: "Press Run scenario when you are ready — results stay on the server.",
    },
    {
      url: "/artifacts/attribution_viewer/index.html#src=sample_aggregate_chain_rumor_depeg.json",
      selector: "#presetSelect",
      title: "4) Ask what caused the collapse",
      body:
        "A replay shows what happened. Attribution shows why — by re-running the simulation with controlled changes.\n\n" +
        "This sample is a mutation chain on the aggregate peg domain: each row adds one change to the stress schedule and reports how much extra instability and attack cost it added. Follow the chain from baseline toward collapse.\n\n" +
        "Use the preset dropdown to switch between bundled attribution samples if you want to compare domains later.",
      hint: "Read the chain table — each step is one added mutation.",
    },
    {
      url: "/artifacts/attribution_viewer/index.html#src=sample_coupled_mutation_chain.json",
      selector: "#panel table, #panel .path-step",
      title: "5) Research fork — mutation chain",
      body:
        "The coupled institution fork is separate from the six charter domains. It models peg panic and infrastructure overload exchanging signals inside a single simulation step.\n\n" +
        "This attribution chain pins one attack schedule and steps up coupling strength. Each row shows how much worse the run gets when panic and overload feed each other more tightly.\n\n" +
        "This is research physics — not part of the stable six-domain workbench charter.",
      hint: "Compare delta instability and cost across coupling mutations.",
    },
    {
      url: "/artifacts/replay_viewer/index.html#src=sample_coupled_institution_replay.json",
      selector: "#cv",
      title: "6) Research fork — coupled replay",
      body:
        "The coupled replay viewer shows two linked signals on one timeline: peg price (blue) and overload (teal dashed), both driven by the same pinned attack schedule.\n\n" +
        "Watch how they move together when coupling is non-zero — a shock that raises panic can also push overload, and vice versa, within the same step.\n\n" +
        "Charter-domain replays only show one world's physics; this fork deliberately couples two.",
      hint: "Scrub the chart and watch peg and overload rise together.",
    },
    {
      url: "/artifacts/coupling_sweep_viewer/index.html",
      selector: "#cv",
      title: "7) Coupling strength sweep",
      body:
        "This chart holds the attack schedule fixed and varies only coupling strength — how tightly peg panic and overload exchange signal each step.\n\n" +
        "Points show integral instability at each coupling level. Red markers mean the run collapsed within the horizon. Use it to see how much coupling alone can worsen outcomes.\n\n" +
        "Open the Presets menu if you need to reload the bundled sweep JSON.",
      hint: "Follow the curve — higher coupling often means higher instability.",
    },
    {
      url: "/artifacts/coupling_comparison_viewer/index.html",
      selector: "#panel .grid",
      title: "8) Coupling comparison (A vs B)",
      body:
        "Here the same pinned schedule is run twice: a baseline coupling level and a higher-coupling variant.\n\n" +
        "The grid shows side-by-side metrics — collapse step, integral instability, attack cost — plus deltas so you can quantify how much worse the tighter coupling made the run.\n\n" +
        "This is the fork's answer to \"what if we only changed coupling, nothing else?\"",
      hint: "Read baseline vs variant columns and the delta row.",
    },
    {
      url: "/artifacts/pareto_viewer/index.html#src=sample_pareto_coupled_institution.json",
      selector: "#cv",
      title: "9) Coupled fork trade-offs (Pareto)",
      body:
        "A Pareto chart plots many attacks at once: severity (how bad the outcome) vs attack cost (how expensive the stress schedule was).\n\n" +
        "Each dot is a non-dominated solution from a genetic search on coupled peg–overload physics. Cheap-but-mild sits on one end; expensive-but-devastating on the other.\n\n" +
        "Co-evolution runs on Run a scenario produce fresh Pareto files under /runs/<id>/.",
      hint: "Each dot is one attack — trace the cost vs severity frontier.",
    },
    {
      url: "/artifacts/composite_viewer/index.html#src=../composite_demo/sample_hexa_composite.json",
      selector: "select, .btn, button",
      title: "Bonus: same attack, six domains",
      body:
        "The composite viewer applies one attack genome across multiple charter domains and shows the scorecard side by side.\n\n" +
        "This hexa sample runs the same schedule on all six reference worlds (peg, network, cascade, backlog, ladder, inventory). Use Presets to switch twin through hexa bundles.\n\n" +
        "Composite output is not a replay timeline — it is a multi-domain audit of one attack.",
      hint: "Try Presets to compare twin, triple, quad, penta, and hexa bundles.",
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
    return sessionStorage.getItem(TOUR_ACTIVE) === "1";
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
    params.delete("tour");
    params.delete("autoplay");
    params.delete("ms");
    var qs2 = params.toString();
    history.replaceState(null, "", window.location.pathname + (qs2 ? "?" + qs2 : "") + window.location.hash);
  }

  function clearAutoplayTimer() {
    if (autoplayTimer) {
      window.clearTimeout(autoplayTimer);
      autoplayTimer = null;
    }
  }

  function teardown() {
    clearAutoplayTimer();
    var root = document.getElementById("fdeTourRoot");
    if (root && root.parentNode) root.parentNode.removeChild(root);
    if (floatExitEl && floatExitEl.parentNode) floatExitEl.parentNode.removeChild(floatExitEl);
    floatExitEl = null;
  }

  function exitTour() {
    clearAutoplayTimer();
    sessionStorage.removeItem(TOUR_ACTIVE);
    sessionStorage.removeItem(TOUR_INDEX);
    sessionStorage.removeItem(TOUR_AUTOPLAY);
    sessionStorage.removeItem(TOUR_PLAYING);
    sessionStorage.removeItem(TOUR_MS);
    sessionStorage.removeItem(TOUR_REDIRECTS);
    sessionStorage.removeItem(TOUR_NAV_TARGET);
    stripTourFromUrl();
    teardown();
  }

  window.fdeExitTour = exitTour;

  function ensureFloatExit() {
    if (floatExitEl) return floatExitEl;
    floatExitEl = document.createElement("button");
    floatExitEl.type = "button";
    floatExitEl.className = "fde-tour-float-exit";
    floatExitEl.textContent = "Exit tour";
    floatExitEl.setAttribute("aria-label", "Exit guided tour");
    floatExitEl.onclick = function () { exitTour(); };
    document.body.appendChild(floatExitEl);
    return floatExitEl;
  }

  function syncToStep(i) {
    var step = steps[i];
    if (!step) return "ok";
    var want = step.url;
    var here = pagePath();
    if (pathsMatch(want, here)) {
      sessionStorage.removeItem(TOUR_REDIRECTS);
      sessionStorage.removeItem(TOUR_NAV_TARGET);
      return "ok";
    }
    var navKey = i + "|" + want;
    if (sessionStorage.getItem(TOUR_NAV_TARGET) === navKey) {
      var redirects = parseInt(sessionStorage.getItem(TOUR_REDIRECTS) || "0", 10);
      if (!isFinite(redirects)) redirects = 0;
      if (redirects >= 4) return "stuck";
      sessionStorage.setItem(TOUR_REDIRECTS, String(redirects + 1));
    } else {
      sessionStorage.setItem(TOUR_NAV_TARGET, navKey);
      sessionStorage.setItem(TOUR_REDIRECTS, "1");
    }
    navigateToStepUrl(want);
    return "navigating";
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

  function tourControlClick(fn) {
    return function (e) { fn(e); };
  }

  function render() {
    if (!isTourActive()) {
      teardown();
      return;
    }
    clearAutoplayTimer();
    teardown();
    ensureFloatExit();

    var i = currentIndex();
    var step = steps[i];
    var sync = syncToStep(i);

    var root = document.createElement("div");
    root.id = "fdeTourRoot";
    root.innerHTML = [
      '<div class="fde-tour-dim" id="fdeTourDim" title="Click to exit tour"></div>',
      '<div class="fde-tour-spot" aria-hidden="true"></div>',
      '<div class="fde-tour-card" role="dialog" aria-label="Guided tour">',
      '  <div class="fde-tour-kicker">Step-by-step tour · Esc to exit</div>',
      '  <div class="fde-tour-title" id="fdeTourTitle"></div>',
      '  <div class="fde-tour-body" id="fdeTourBody"></div>',
      '  <div class="fde-tour-caption" id="fdeTourCaption"></div>',
      '  <div class="fde-tour-progress-wrap"><div class="fde-tour-progress-bar" id="fdeTourBar"></div></div>',
      '  <div class="fde-tour-controls">',
      '    <button type="button" class="fde-tour-btn" id="fdeTourBack">Back</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-primary" id="fdeTourNext">Next</button>',
      '    <button type="button" class="fde-tour-btn" id="fdeTourPlay">Pause</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-ghost" id="fdeTourExit">Exit tour</button>',
      '  </div>',
      '  <div class="fde-tour-progress" id="fdeTourProgress"></div>',
      "</div>",
    ].join("");
    document.body.appendChild(root);

    var bodyText = step.body;
    if (sync === "navigating") bodyText = "Taking you to the next screen… " + bodyText;
    if (sync === "stuck") {
      bodyText =
        "This step could not load automatically. Use Next when ready, or Exit tour (top-right, Esc, or click the dark backdrop). " +
        bodyText;
    }

    setText(document.getElementById("fdeTourTitle"), step.title);
    setBodyHtml(document.getElementById("fdeTourBody"), bodyText);
    var capEl = document.getElementById("fdeTourCaption");
    if (step.hint && sync === "ok") {
      setText(capEl, "Look for: " + step.hint);
      if (capEl) capEl.style.display = "";
    } else if (capEl) {
      capEl.textContent = "";
      capEl.style.display = "none";
    }
    setText(document.getElementById("fdeTourProgress"), (i + 1) + " / " + steps.length);

    var dim = document.getElementById("fdeTourDim");
    var back = document.getElementById("fdeTourBack");
    var next = document.getElementById("fdeTourNext");
    var play = document.getElementById("fdeTourPlay");
    var exit = document.getElementById("fdeTourExit");

    if (dim) dim.onclick = tourControlClick(function () { exitTour(); });
    if (back) {
      back.disabled = i <= 0;
      back.onclick = tourControlClick(function () {
        setIndex(i - 1);
        render();
      });
    }
    if (next) {
      next.textContent = (i >= steps.length - 1) ? "Finish" : "Next";
      next.onclick = tourControlClick(function () {
        if (i >= steps.length - 1) {
          exitTour();
          return;
        }
        setIndex(i + 1);
        render();
      });
    }
    if (play) {
      if (sessionStorage.getItem(TOUR_AUTOPLAY) === "1") {
        play.style.display = "";
        play.textContent = isPlaying() ? "Pause" : "Play";
        play.onclick = tourControlClick(function () {
          setPlaying(!isPlaying());
          render();
        });
      } else {
        play.style.display = "none";
      }
    }
    if (exit) exit.onclick = tourControlClick(function () { exitTour(); });

    function position() {
      if (sync !== "ok") return;
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

    if (sync === "navigating") return;

    var autoplay = sessionStorage.getItem(TOUR_AUTOPLAY) === "1";
    if (autoplay && sync === "ok") {
      var ms = parseInt(sessionStorage.getItem(TOUR_MS) || "8000", 10);
      if (!isFinite(ms)) ms = 8000;
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
      autoplayTimer = window.setTimeout(function () {
        if (!isTourActive()) return;
        if (currentIndex() !== i) return;
        if (!isPlaying()) return;
        if (i >= steps.length - 1) {
          exitTour();
          return;
        }
        setIndex(i + 1);
        render();
      }, ms);
    }
  }

  function onTourEscape(e) {
    if (e.key === "Escape") exitTour();
  }

  ensureTourStartedFromUrl();
  if (!isTourActive()) return;
  if (!isTourPage()) {
    exitTour();
    return;
  }
  document.addEventListener("keydown", onTourEscape);
  window.addEventListener("hashchange", function () {
    if (isTourActive()) render();
  });
  if (!sessionStorage.getItem(TOUR_INDEX)) sessionStorage.setItem(TOUR_INDEX, "0");
  render();
})();
