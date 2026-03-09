/**
 * ATS Resume Analyzer — Background Service Worker
 *
 * Handles extension lifecycle events and message passing.
 */

// Set default API URL on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["apiUrl"], (result) => {
    if (!result.apiUrl) {
      chrome.storage.local.set({ apiUrl: "http://localhost:8000" });
    }
  });

  console.log("[ATS Analyzer] Extension installed.");
});
