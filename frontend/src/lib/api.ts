/** API client for the ATS Resume Analyzer backend — v2. */

import { AnalysisResult, ResumeStrengthResult } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(err.detail || "An error occurred", response.status);
  }
  return response.json();
}

/** Analyse a resume file against a job description. */
export async function analyzeResume(
  file: File,
  jobDescription: string,
): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("resume", file);
  form.append("job_description", jobDescription);
  const res = await fetch(`${API_URL}/analyze`, { method: "POST", body: form });
  return handleResponse<AnalysisResult>(res);
}

/** Analyse resume text (no file upload). */
export async function analyzeResumeText(
  resumeText: string,
  jobDescription: string,
): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/analyze-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
  });
  return handleResponse<AnalysisResult>(res);
}

/** Analyse resume without a JD (Feature 6). */
export async function analyzeResumeOnly(
  resumeText: string,
): Promise<ResumeStrengthResult> {
  const res = await fetch(`${API_URL}/analyze-resume-only`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText }),
  });
  return handleResponse<ResumeStrengthResult>(res);
}

/** Analyse a resume file without a JD (Feature 6 — file variant). */
export async function analyzeResumeFileOnly(
  file: File,
): Promise<ResumeStrengthResult> {
  // Read the file as text on the client (simple approach for now)
  const text = await file.text();
  return analyzeResumeOnly(text);
}

/** Health check. */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
