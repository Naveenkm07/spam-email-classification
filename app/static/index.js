(function () {
  "use strict";

  function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function initThemeToggle() {
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    const root = document.documentElement;
    const stored = window.localStorage.getItem("theme");
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = stored || (prefersDark ? "dark" : "light");

    function applyTheme(theme) {
      root.dataset.theme = theme;
      toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      window.localStorage.setItem("theme", theme);
    }

    applyTheme(initial);

    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }

  function attachHtml5Validation(form) {
    if (!form) return;

    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
      }
    });
  }

  function initFormValidation() {
    attachHtml5Validation(document.getElementById("signin-form"));
    attachHtml5Validation(document.getElementById("signup-form"));
    attachHtml5Validation(document.getElementById("predict-form"));
  }

  function initRealtimePrediction() {
    const form = document.getElementById("predict-form");
    const textarea = document.getElementById("message");
    const resultEl = document.getElementById("realtime-result");
    const bar = document.getElementById("confidence-bar");
    const statusEl = document.getElementById("realtime-status");

    if (!form || !textarea || !resultEl || !bar || !statusEl) {
      return;
    }

    let currentController = null;

    function setLoading(isLoading) {
      if (isLoading) {
        statusEl.textContent = "Analyzing...";
        resultEl.setAttribute("data-loading", "true");
      } else {
        resultEl.removeAttribute("data-loading");
      }
    }

    function updateConfidence(prediction, probability) {
      const percent = Math.round(probability * 100);
      statusEl.textContent = `${prediction.toUpperCase()} (${percent}%)`;
      bar.style.width = `${percent}%`;
      bar.setAttribute("aria-valuenow", String(percent));
      bar.setAttribute("data-prediction", prediction);
    }

    const sendRequest = debounce(async function () {
      const text = textarea.value.trim();
      if (!text) {
        statusEl.textContent = "";
        bar.style.width = "0%";
        return;
      }

      if (currentController) {
        currentController.abort();
      }
      currentController = new AbortController();

      setLoading(true);

      try {
        const response = await fetch("/api/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
          signal: currentController.signal,
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || !data || typeof data.probability !== "number") {
          statusEl.textContent = data.error || "Unable to get prediction.";
          bar.style.width = "0%";
          return;
        }

        updateConfidence(data.prediction || "spam", data.probability);
      } catch (error) {
        if (error.name === "AbortError") {
          return;
        }
        statusEl.textContent = "Network error during prediction.";
        bar.style.width = "0%";
      } finally {
        setLoading(false);
      }
    }, 300);

    textarea.addEventListener("input", sendRequest);
  }

  document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initFormValidation();
    initRealtimePrediction();
  });
})();
