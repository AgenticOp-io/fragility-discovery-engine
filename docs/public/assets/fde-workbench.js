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

/** Guided tour overlay (manual + autoplay + optional voice narration). */
(function () {
  var TOUR_ACTIVE = "fde_tour_active_v1";
  var TOUR_INDEX = "fde_tour_index_v1";
  var TOUR_AUTOPLAY = "fde_tour_autoplay_v1";
  var TOUR_MS = "fde_tour_ms_v1";
  var TOUR_PLAYING = "fde_tour_playing_v1";
  var TOUR_VOICE = "fde_tour_voice_v1";
  var TOUR_VOICE_MUTED = "fde_tour_voice_muted_v1";
  var TOUR_VOICE_UNLOCKED = "fde_tour_voice_unlocked_v1";
  var TOUR_REDIRECTS = "fde_tour_redirects_v1";
  var TOUR_NAV_TARGET = "fde_tour_nav_target_v1";
  var floatExitEl = null;
  var autoplayTimer = null;
  var voicesReady = false;

  function qs(sel) {
    try { return document.querySelector(sel); } catch (e) { return null; }
  }
  function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
  function setText(el, txt) { if (el) el.textContent = String(txt || ""); }

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
    var changed = params.has("tour") || params.has("autoplay") || params.has("voice") || params.has("ms");
    if (!changed) return;
    params.delete("tour");
    params.delete("autoplay");
    params.delete("voice");
    params.delete("ms");
    var qs = params.toString();
    history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : "") + normalizeHash(window.location.hash || ""));
  }

  function navigateToStepUrl(want) {
    stopSpeech();
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
      body: "Open the flagship replay. Then step the timeline to see exactly when the system crosses its breaking point.",
      say: "Step one: watch a collapse. Open the flagship replay, then step through the timeline to see when the system breaks.",
    },
    {
      url: "/artifacts/replay_viewer/index.html#src=sample_replay.json",
      selector: "canvas",
      title: "Replay timeline",
      body: "Drag or click on the chart to scrub through time. Look for the collapse marker and the instability curve.",
      say: "Scrub the replay chart. Drag or click to move through time and watch instability rise toward collapse.",
    },
    {
      url: "/run.html",
      selector: "#runBtn",
      title: "2) Run a live search",
      body: "Keep the defaults and press Run scenario. The server will search for a worst-case schedule and open the results.",
      say: "Step two: run a live search. Keep the defaults and press Run scenario. The server finds a stressful schedule and opens the results.",
    },
    {
      url: "/artifacts/attribution_viewer/index.html#src=sample_aggregate_chain_rumor_depeg.json",
      selector: "#presetSelect",
      title: "3) Ask what caused it",
      body: "This view shows a mutation chain: each step adds one change and shows its delta instability and delta cost.",
      say: "Step three: ask what caused it. Each link in the chain adds one mutation and shows how much instability and cost it added.",
    },
    {
      url: "/artifacts/attribution_viewer/index.html#src=sample_coupled_mutation_chain.json",
      selector: "#panel table, #panel .path-step",
      title: "4) Coupled fork chain",
      body: "Research fork: peg panic and overload exchange signals each step. Coupling strength mutations stack on a pinned schedule — not the six-domain composite.",
      say: "Step four: the coupled research fork. Coupling strength steps up on a pinned schedule while panic and overload trade signals inside one simulation step.",
    },
    {
      url: "/artifacts/composite_viewer/index.html#src=../composite_demo/sample_hexa_composite.json",
      selector: "select, .btn, button",
      title: "Bonus: compare all six domains",
      body: "The composite view applies the same attack to every domain side by side. Try presets to switch bundles.",
      say: "Bonus: compare all six domains. The same attack runs on every reference world side by side.",
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
  function voiceEnabled() { return sessionStorage.getItem(TOUR_VOICE) === "1"; }
  function setVoiceEnabled(v) { sessionStorage.setItem(TOUR_VOICE, v ? "1" : "0"); }
  function isVoiceMuted() { return sessionStorage.getItem(TOUR_VOICE_MUTED) === "1"; }
  function setVoiceMuted(v) { sessionStorage.setItem(TOUR_VOICE_MUTED, v ? "1" : "0"); }

  function isTourActive() {
    return sessionStorage.getItem(TOUR_ACTIVE) === "1";
  }

  function speechSupported() {
    return !!(window.speechSynthesis && window.SpeechSynthesisUtterance);
  }

  function voiceUnlocked() {
    return sessionStorage.getItem(TOUR_VOICE_UNLOCKED) === "1";
  }

  function unlockVoice() {
    sessionStorage.setItem(TOUR_VOICE_UNLOCKED, "1");
    if (!window.speechSynthesis) return;
    try {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.resume();
    } catch (e) {}
  }

  function prepareVoices() {
    if (!speechSupported() || voicesReady) return;
    function load() {
      voicesReady = window.speechSynthesis.getVoices().length > 0;
    }
    load();
    window.speechSynthesis.onvoiceschanged = load;
  }

  function stopSpeech() {
    if (!window.speechSynthesis) return;
    try { window.speechSynthesis.cancel(); } catch (e) {}
  }

  function speechLine(step) {
    if (step.say) return step.say;
    return step.title + ". " + step.body;
  }

  function pickVoice(utterance) {
    if (!window.speechSynthesis) return;
    var voices = window.speechSynthesis.getVoices();
    var en = voices.filter(function (v) { return /^en(-|_)/i.test(v.lang); });
    if (en.length) utterance.voice = en[0];
  }

  function speakStep(step) {
    if (!voiceEnabled() || isVoiceMuted() || !speechSupported() || !voiceUnlocked()) return;
    stopSpeech();
    prepareVoices();
    var u = new SpeechSynthesisUtterance(speechLine(step));
    u.lang = "en-US";
    u.rate = 0.98;
    u.pitch = 1.0;
    pickVoice(u);
    try { window.speechSynthesis.speak(u); } catch (e) {}
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
    var voice = params.get("voice");
    if (voice === "1" || ap === "1") setVoiceEnabled(true);
    if (voice === "0") setVoiceEnabled(false);
    var ms = parseInt(params.get("ms") || "", 10);
    if (isFinite(ms) && ms >= 1500) sessionStorage.setItem(TOUR_MS, String(ms));
    params.delete("tour");
    params.delete("autoplay");
    params.delete("voice");
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
    stopSpeech();
    var root = document.getElementById("fdeTourRoot");
    if (root && root.parentNode) root.parentNode.removeChild(root);
    if (floatExitEl && floatExitEl.parentNode) floatExitEl.parentNode.removeChild(floatExitEl);
    floatExitEl = null;
  }

  function exitTour() {
    clearAutoplayTimer();
    stopSpeech();
    sessionStorage.removeItem(TOUR_ACTIVE);
    sessionStorage.removeItem(TOUR_INDEX);
    sessionStorage.removeItem(TOUR_AUTOPLAY);
    sessionStorage.removeItem(TOUR_PLAYING);
    sessionStorage.removeItem(TOUR_MS);
    sessionStorage.removeItem(TOUR_VOICE);
    sessionStorage.removeItem(TOUR_VOICE_MUTED);
    sessionStorage.removeItem(TOUR_VOICE_UNLOCKED);
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
    return function (e) {
      unlockVoice();
      fn(e);
    };
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
      '  <div class="fde-tour-kicker">Tour · Esc to exit</div>',
      '  <div class="fde-tour-title" id="fdeTourTitle"></div>',
      '  <div class="fde-tour-body" id="fdeTourBody"></div>',
      '  <div class="fde-tour-caption" id="fdeTourCaption"></div>',
      '  <div class="fde-tour-progress-wrap"><div class="fde-tour-progress-bar" id="fdeTourBar"></div></div>',
      '  <div class="fde-tour-controls">',
      '    <button type="button" class="fde-tour-btn" id="fdeTourBack">Back</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-primary" id="fdeTourNext">Next</button>',
      '    <button type="button" class="fde-tour-btn" id="fdeTourPlay">Pause</button>',
      '    <button type="button" class="fde-tour-btn fde-tour-voice-play" id="fdeTourSpeak">Play voice</button>',
      '    <button type="button" class="fde-tour-btn" id="fdeTourVoice">Mute voice</button>',
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
    setText(document.getElementById("fdeTourBody"), bodyText);
    var cap = speechLine(step);
    if (voiceEnabled() && !voiceUnlocked()) {
      cap = "Tap Play voice once (browser requires a click to speak). " + cap;
    }
    setText(document.getElementById("fdeTourCaption"), cap);
    setText(document.getElementById("fdeTourProgress"), (i + 1) + " / " + steps.length);

    var dim = document.getElementById("fdeTourDim");
    var back = document.getElementById("fdeTourBack");
    var next = document.getElementById("fdeTourNext");
    var play = document.getElementById("fdeTourPlay");
    var speak = document.getElementById("fdeTourSpeak");
    var voiceBtn = document.getElementById("fdeTourVoice");
    var exit = document.getElementById("fdeTourExit");

    if (dim) dim.onclick = tourControlClick(function () { exitTour(); });
    if (back) {
      back.disabled = i <= 0;
      back.onclick = tourControlClick(function () {
        stopSpeech();
        setIndex(i - 1);
        render();
      });
    }
    if (next) {
      next.textContent = (i >= steps.length - 1) ? "Finish" : "Next";
      next.onclick = tourControlClick(function () {
        stopSpeech();
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
          if (isPlaying()) stopSpeech();
          setPlaying(!isPlaying());
          render();
        });
      } else {
        play.style.display = "none";
      }
    }
    if (speak) {
      if (!speechSupported()) {
        speak.style.display = "none";
      } else {
        speak.style.display = "";
        speak.textContent = voiceUnlocked() ? "Replay voice" : "Play voice";
        speak.onclick = tourControlClick(function () {
          setVoiceEnabled(true);
          setVoiceMuted(false);
          unlockVoice();
          speakStep(step);
        });
      }
    }
    if (voiceBtn) {
      if (!speechSupported()) {
        voiceBtn.style.display = "none";
      } else if (!voiceEnabled()) {
        voiceBtn.textContent = "Voice off";
        voiceBtn.classList.remove("fde-tour-muted");
        voiceBtn.onclick = tourControlClick(function () {
          setVoiceEnabled(true);
          setVoiceMuted(false);
          render();
        });
      } else if (isVoiceMuted()) {
        voiceBtn.textContent = "Unmute voice";
        voiceBtn.classList.add("fde-tour-muted");
        voiceBtn.onclick = tourControlClick(function () {
          setVoiceMuted(false);
          unlockVoice();
          speakStep(step);
          render();
        });
      } else {
        voiceBtn.textContent = "Mute voice";
        voiceBtn.classList.remove("fde-tour-muted");
        voiceBtn.onclick = tourControlClick(function () {
          setVoiceMuted(true);
          stopSpeech();
          render();
        });
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

    if (voiceEnabled() && !isVoiceMuted() && voiceUnlocked()) {
      window.setTimeout(function () {
        if (isTourActive()) speakStep(step);
      }, 200);
    }

    var autoplay = sessionStorage.getItem(TOUR_AUTOPLAY) === "1";
    if (autoplay && sync === "ok") {
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

  prepareVoices();
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
