/**
 * ATS Resume Analyzer — Content Script
 *
 * Injected into job listing pages to detect and extract job descriptions.
 * Adds a floating button for quick extraction.
 */

(function () {
  "use strict";

  // Avoid double-injection
  if (window.__atsAnalyzerInjected) return;
  window.__atsAnalyzerInjected = true;

  /**
   * Detect the current job site and return relevant selectors.
   */
  function getJobDescriptionSelector() {
    const hostname = window.location.hostname;

    if (hostname.includes("linkedin.com")) {
      return [
        ".jobs-description__content",
        ".jobs-description-content__text",
        ".jobs-box__html-content",
        "#job-details",
      ];
    }

    if (hostname.includes("indeed.com")) {
      return [
        "#jobDescriptionText",
        ".jobsearch-jobDescriptionText",
      ];
    }

    if (hostname.includes("glassdoor.com")) {
      return [
        ".jobDescriptionContent",
        '[class*="JobDescription"]',
      ];
    }

    if (hostname.includes("monster.com")) {
      return [
        ".job-description",
        '[class*="jobDescription"]',
      ];
    }

    return [];
  }

  /**
   * Extract job description from the page.
   */
  function extractJobDescription() {
    const selectors = getJobDescriptionSelector();

    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el) {
        const text = el.innerText.trim();
        if (text.length > 100) return text;
      }
    }

    return null;
  }

  /**
   * Listen for messages from the popup.
   */
  chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.action === "extractJobDescription") {
      const text = extractJobDescription();
      sendResponse({ jobDescription: text });
    }
    return true;
  });

  // Notify that content script is ready
  console.log("[ATS Analyzer] Content script loaded on", window.location.hostname);
})();
