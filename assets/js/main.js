(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");

  /* ---- header shadow on scroll */
  var header = document.querySelector(".site-header");
  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 30);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- mobile nav */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) toggle.click();
    });
  }

  /* ---- reveal on scroll */
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- countdown */
  var cd = document.querySelector("[data-countdown]");
  if (cd) {
    var target = new Date(cd.getAttribute("data-countdown")).getTime();
    var parts = {
      d: cd.querySelector("[data-d]"), h: cd.querySelector("[data-h]"),
      m: cd.querySelector("[data-m]"), s: cd.querySelector("[data-s]")
    };
    var pad = function (n) { return n < 10 ? "0" + n : String(n); };
    var tick = function () {
      var diff = Math.max(0, target - Date.now());
      var s = Math.floor(diff / 1000);
      parts.d.textContent = Math.floor(s / 86400);
      parts.h.textContent = pad(Math.floor((s % 86400) / 3600));
      parts.m.textContent = pad(Math.floor((s % 3600) / 60));
      parts.s.textContent = pad(s % 60);
    };
    tick();
    setInterval(tick, 1000);
  }

  /* ---- RSVP
     Set data-endpoint on the form to a form service URL (e.g. Formspree) to
     collect responses online. Without one, the reply opens as a pre-filled
     email to the address in data-email. */
  var form = document.querySelector("#rsvp-form");
  if (form) {
    var attending = form.querySelectorAll('input[name="attending"]');
    var whenYes = form.querySelectorAll("[data-if-yes]");
    var sync = function () {
      var yes = form.querySelector('input[name="attending"]:checked');
      var show = !yes || yes.value === "Joyfully accepts";
      whenYes.forEach(function (el) { el.hidden = !show; });
    };
    attending.forEach(function (r) { r.addEventListener("change", sync); });
    sync();

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var data = new FormData(form);
      var events = data.getAll("events").join(", ");
      var thanks = document.querySelector("#rsvp-thanks");
      var done = function () {
        form.hidden = true;
        thanks.hidden = false;
        thanks.scrollIntoView({ behavior: "smooth", block: "center" });
      };

      var endpoint = form.getAttribute("data-endpoint");
      if (endpoint) {
        var btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = "Sending…";
        fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
          .then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
          .catch(function () {
            btn.disabled = false;
            btn.textContent = "Send RSVP";
            alert("Sorry, your RSVP could not be sent. Please try again in a moment.");
          });
        return;
      }

      var lines = [
        "Name: " + data.get("name"),
        "Email: " + data.get("email"),
        "Phone: " + (data.get("phone") || "-"),
        "Response: " + data.get("attending")
      ];
      if (data.get("attending") === "Joyfully accepts") {
        lines.push("Guests: " + data.get("guests"));
        lines.push("Attending: " + (events || "-"));
        lines.push("Dietary: " + (data.get("diet") || "-"));
      }
      lines.push("", "Message:", data.get("message") || "-");
      var subject = "RSVP — " + data.get("name") + " (" + data.get("attending") + ")";
      window.location.href = "mailto:" + form.getAttribute("data-email") +
        "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
      done();
    });
  }
})();
