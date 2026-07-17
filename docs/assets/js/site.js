// VoidTorrent site interactions
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- scroll reveal ----
  var reveals = document.querySelectorAll(".reveal, .feature, .step");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // ---- nav scrolled state ----
  var nav = document.querySelector(".nav");
  var progress = document.getElementById("progress");
  function onScroll() {
    if (nav) nav.classList.toggle("scrolled", window.scrollY > 12);
    if (progress) {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
      progress.style.width = pct.toFixed(2) + "%";
    }
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // ---- animated counters (with optional suffix) ----
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-target")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var dur = 1500, start = null;
    function tick(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = target * eased;
      var shown = (target % 1 === 0) ? Math.round(val) : val.toFixed(1);
      el.innerHTML = shown + '<span class="suffix">' + suffix + "</span>";
      if (p < 1) requestAnimationFrame(tick);
      else el.innerHTML = target + '<span class="suffix">' + suffix + "</span>";
    }
    if (reduceMotion) { el.innerHTML = target + '<span class="suffix">' + suffix + "</span>"; return; }
    requestAnimationFrame(tick);
  }
  var counters = document.querySelectorAll(".counter");
  if (counters.length && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animateCount(e.target); cio.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  // ---- live hero mock: subtle speed flicker ----
  var mockRows = document.querySelectorAll(".mock-row");
  if (!reduceMotion && mockRows.length) {
    var metas = document.querySelectorAll(".mock-meta b");
    var base = [68, 34];
    setInterval(function () {
      metas.forEach(function (m, i) {
        if (i >= base.length) return;
        var v = (base[i] * (0.9 + Math.random() * 0.2)).toFixed(0);
        m.textContent = v + "%";
      });
      mockRows.forEach(function (r, i) {
        if (i === 1) return;
        var bar = r.querySelector(".mock-prog span");
        if (!bar) return;
        var w = parseFloat(bar.style.width) || 0;
        if (w < 100) { w = Math.min(100, w + Math.random() * 1.4); bar.style.width = w.toFixed(1) + "%"; }
      });
    }, 1400);
  }

  // ---- button ripple ----
  document.querySelectorAll(".btn-accent, .btn").forEach(function (b) {
    b.addEventListener("click", function (e) {
      var r = b.getBoundingClientRect();
      var rip = document.createElement("span");
      rip.className = "ripple";
      var size = Math.max(r.width, r.height);
      rip.style.width = rip.style.height = size + "px";
      rip.style.left = (e.clientX - r.left - size / 2) + "px";
      rip.style.top = (e.clientY - r.top - size / 2) + "px";
      b.appendChild(rip);
      setTimeout(function () { rip.remove(); }, 600);
    });
  });
})();
