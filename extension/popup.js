/**
 * ATS Resume Analyzer — Extension Popup Script
 *
 * Handles UI interactions, API communication, and result display.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const apiUrlInput = document.getElementById("apiUrl");
  const saveSettingsBtn = document.getElementById("saveSettings");
  const extractBtn = document.getElementById("extractBtn");
  const jobDescriptionEl = document.getElementById("jobDescription");
  const resumeTextEl = document.getElementById("resumeText");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultsSection = document.getElementById("resultsSection");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const errorMessage = document.getElementById("errorMessage");
  const scoreCircle = document.getElementById("scoreCircle");
  const scoreValue = document.getElementById("scoreValue");
  const keywordScore = document.getElementById("keywordScore");
  const semanticScore = document.getElementById("semanticScore");
  const matchedKeywords = document.getElementById("matchedKeywords");
  const missingKeywords = document.getElementById("missingKeywords");
  const suggestionsList = document.getElementById("suggestionsList");

  // Load saved settings
  chrome.storage.local.get(["apiUrl"], (result) => {
    if (result.apiUrl) {
      apiUrlInput.value = result.apiUrl;
    }
  });

  // Save settings
  saveSettingsBtn.addEventListener("click", () => {
    const url = apiUrlInput.value.trim().replace(/\/+$/, "");
    chrome.storage.local.set({ apiUrl: url }, () => {
      saveSettingsBtn.textContent = "Saved!";
      setTimeout(() => {
        saveSettingsBtn.textContent = "Save";
      }, 1500);
    });
  });

  // Enable/disable analyze button
  function updateAnalyzeButton() {
    const hasJd = jobDescriptionEl.value.trim().length >= 50;
    const hasResume = resumeTextEl.value.trim().length >= 50;
    analyzeBtn.disabled = !(hasJd && hasResume);
  }

  jobDescriptionEl.addEventListener("input", updateAnalyzeButton);
  resumeTextEl.addEventListener("input", updateAnalyzeButton);

  // Extract job description from page
  extractBtn.addEventListener("click", async () => {
    try {
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      if (!tab?.id) {
        showError("No active tab found.");
        return;
      }

      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: extractJobDescription,
      });

      if (results && results[0]?.result) {
        jobDescriptionEl.value = results[0].result;
        updateAnalyzeButton();
        hideError();
      } else {
        showError(
          "Could not extract job description from this page. Try pasting it manually."
        );
      }
    } catch (err) {
      showError(
        "Cannot extract from this page. Make sure you're on a job listing page."
      );
      console.error("Extraction error:", err);
    }
  });

  // Analyze button click
  analyzeBtn.addEventListener("click", async () => {
    const apiUrl = apiUrlInput.value.trim().replace(/\/+$/, "");
    const jobDesc = jobDescriptionEl.value.trim();
    const resume = resumeTextEl.value.trim();

    if (!jobDesc || !resume) return;

    showLoading();
    hideError();
    resultsSection.classList.add("hidden");

    try {
      const response = await fetch(`${apiUrl}/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: resume,
          job_description: jobDesc,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      displayResults(data);
    } catch (err) {
      showError(
        err.message ||
          "Failed to connect to the API. Make sure the backend is running."
      );
    } finally {
      hideLoading();
    }
  });

  // Display results
  function displayResults(data) {
    resultsSection.classList.remove("hidden");

    // Score circle
    const score = data.ats_score;
    scoreValue.textContent = `${score}%`;

    scoreCircle.className = "score-circle";
    if (score >= 75) scoreCircle.classList.add("excellent");
    else if (score >= 50) scoreCircle.classList.add("good");
    else scoreCircle.classList.add("poor");

    // Breakdown scores
    keywordScore.textContent = `${data.keyword_match_score}%`;
    semanticScore.textContent = `${data.semantic_similarity_score}%`;

    // Matched keywords
    matchedKeywords.innerHTML = "";
    (data.matched_keywords || []).forEach((kw) => {
      const tag = document.createElement("span");
      tag.className = "keyword-tag matched";
      tag.textContent = kw;
      matchedKeywords.appendChild(tag);
    });

    // Missing keywords
    missingKeywords.innerHTML = "";
    (data.missing_keywords || []).forEach((kw) => {
      const tag = document.createElement("span");
      tag.className = "keyword-tag missing";
      tag.textContent = kw;
      missingKeywords.appendChild(tag);
    });

    // Suggestions
    suggestionsList.innerHTML = "";
    (data.suggestions || []).slice(0, 5).forEach((suggestion) => {
      const li = document.createElement("li");
      li.textContent = suggestion;
      suggestionsList.appendChild(li);
    });

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  // Helper functions
  function showLoading() {
    loadingOverlay.classList.remove("hidden");
  }

  function hideLoading() {
    loadingOverlay.classList.add("hidden");
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.classList.remove("hidden");
  }

  function hideError() {
    errorMessage.classList.add("hidden");
  }
});

/**
 * Extracts job description text from the current page.
 * Runs as a content script in the active tab.
 */
function extractJobDescription() {
  // LinkedIn selectors
  const linkedInSelectors = [
    ".jobs-description__content",
    ".jobs-description-content__text",
    ".jobs-box__html-content",
    '[class*="jobs-description"]',
    "#job-details",
  ];

  // Indeed selectors
  const indeedSelectors = [
    "#jobDescriptionText",
    ".jobsearch-jobDescriptionText",
    '[class*="jobDescription"]',
  ];

  // Glassdoor selectors
  const glassdoorSelectors = [
    ".jobDescriptionContent",
    '[class*="JobDescription"]',
    ".desc",
  ];

  // Generic selectors (fallback)
  const genericSelectors = [
    '[class*="job-description"]',
    '[class*="jobDescription"]',
    '[class*="job_description"]',
    '[id*="job-description"]',
    '[id*="jobDescription"]',
    '[data-testid*="description"]',
    "article",
    '[role="main"]',
  ];

  const allSelectors = [
    ...linkedInSelectors,
    ...indeedSelectors,
    ...glassdoorSelectors,
    ...genericSelectors,
  ];

  for (const selector of allSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      const text = element.innerText.trim();
      if (text.length > 100) {
        return text;
      }
    }
  }

  // Last resort: try to get the largest text block on the page
  const allElements = document.querySelectorAll("div, section, article");
  let longestText = "";
  allElements.forEach((el) => {
    const text = el.innerText.trim();
    if (text.length > longestText.length && text.length > 200) {
      longestText = text;
    }
  });

  return longestText || null;
}
