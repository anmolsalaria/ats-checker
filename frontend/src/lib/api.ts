/** API client for the ATS Resume Analyzer backend. */

import { AnalysisResult } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Analyze a resume file against a job description.
 */
export async function analyzeResume(
  file: File,
  jobDescription: string
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
    throw new ApiError(
      error.detail || "An error occurred during analysis",
      response.status
    );
  }

  return response.json();
}

/**
 * Analyze resume text directly (without file upload).
 */
export async function analyzeResumeText(
  resumeText: string,
  jobDescription: string
): Promise<AnalysisResult> {
  const response = await fetch(`${API_URL}/analyze-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
    throw new ApiError(
      error.detail || "An error occurred during analysis",
      response.status
    );
  }

  return response.json();
}

/**
 * Check backend health.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
