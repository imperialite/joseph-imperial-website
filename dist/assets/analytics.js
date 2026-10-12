"use strict";

(() => {
  const measurementId = document.currentScript?.dataset.measurementId;
  if (!/^G-[A-Z0-9]+$/.test(measurementId || "")) return;

  // The public build includes this loader once, on the chosen homepage only.
  if (document.querySelector("script[data-academic-google-tag]")) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  function pageAddress(value) {
    if (!value) return "";
    try {
      const url = new URL(value);
      return url.origin + url.pathname;
    } catch {
      return "";
    }
  }

  window.gtag("js", new Date());
  window.gtag("config", measurementId, {
    send_page_view: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    page_location: pageAddress(window.location.href),
    page_referrer: pageAddress(document.referrer)
  });

  const tag = document.createElement("script");
  tag.async = true;
  tag.dataset.academicGoogleTag = "true";
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
  document.head.append(tag);
})();
