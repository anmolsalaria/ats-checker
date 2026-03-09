"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import JobDescriptionInput from "@/components/JobDescriptionInput";
import AnalysisAnimation from "@/components/AnalysisAnimation";
import {
  analyzeResume,
  analyzeResumeFileOnly,
  analyzeLinkedIn,
  ApiError,
} from "@/lib/api";
import { AnalysisResult, ResumeStrengthResult } from "@/types";
import {
  FileText,
  Zap,
  Target,
  TrendingUp,
  Award,
  Link2,
} from "lucide-react";

type InputMode = "jd" | "linkedin" | "none";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputMode, setInputMode] = useState<InputMode>("jd");

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload a resume.");
      return;
    }

    if (inputMode === "jd" && jobDescription.trim().length < 50) {
      setError("Job description must be at least 50 characters.");
      return;
    }

    if (inputMode === "linkedin" && !linkedinUrl.trim()) {
      setError("Please paste a LinkedIn job URL.");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    const animStart = Date.now();

    try {
      if (inputMode === "none") {
        // Resume strength mode (Feature 8)
        const resultData = await analyzeResumeFileOnly(file);
        const elapsed = Date.now() - animStart;
        if (elapsed < 2500)
          await new Promise((r) => setTimeout(r, 2500 - elapsed));
        sessionStorage.setItem("strengthResult", JSON.stringify(resultData));
        sessionStorage.removeItem("analysisResult");
        router.push("/results");
      } else if (inputMode === "linkedin") {
        // LinkedIn import mode (Feature 10)
        const text = await file.text();
        const resultData = await analyzeLinkedIn(linkedinUrl, text);
        const elapsed = Date.now() - animStart;
        if (elapsed < 2500)
          await new Promise((r) => setTimeout(r, 2500 - elapsed));
        sessionStorage.setItem("analysisResult", JSON.stringify(resultData));
        sessionStorage.removeItem("strengthResult");
        router.push("/results");
      } else {
        // Standard JD mode
        const resultData = await analyzeResume(file, jobDescription);
        const elapsed = Date.now() - animStart;
        if (elapsed < 2500)
          await new Promise((r) => setTimeout(r, 2500 - elapsed));
        sessionStorage.setItem("analysisResult", JSON.stringify(resultData));
        sessionStorage.removeItem("strengthResult");
        router.push("/results");
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to connect to the server. Is the backend running?");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const canSubmit = () => {
    if (!file) return false;
    if (inputMode === "jd" && !jobDescription.trim()) return false;
    if (inputMode === "linkedin" && !linkedinUrl.trim()) return false;
    return true;
  };

  return (
    <div className="page-transition">
      {/* Animated overlay (Feature 11) */}
      <AnalysisAnimation isActive={isAnalyzing} />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 py-20 text-white">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
            AI ATS Resume Analyzer
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-primary-100">
            Optimize your resume for Applicant Tracking Systems. Get instant
            feedback on keyword matching, skill gaps, bullet quality, and
            actionable suggestions.
          </p>
        </div>
      </section>

      {/* Feature cards */}
      <section className="mx-auto -mt-10 max-w-5xl px-4">
        <div className="grid gap-4 sm:grid-cols-5">
          {[
            {
              icon: FileText,
              title: "Upload Resume",
              desc: "PDF or DOCX",
            },
            {
              icon: Target,
              title: "ATS Score",
              desc: "5-factor weighted model",
            },
            {
              icon: Zap,
              title: "Keyword Match",
              desc: "Curated skill dictionary",
            },
            {
              icon: Award,
              title: "Bullet Quality",
              desc: "Action + tech + metrics",
            },
            {
              icon: TrendingUp,
              title: "Suggestions",
              desc: "Actionable improvements",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="card flex flex-col items-center text-center"
            >
              <f.icon className="mb-2 h-8 w-8 text-primary-600" />
              <h3 className="font-semibold text-gray-900">{f.title}</h3>
              <p className="text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Analysis form */}
      <section className="mx-auto max-w-4xl px-4 py-16">
        <div className="card">
          <h2 className="mb-6 text-2xl font-bold text-gray-900">
            Analyze Your Resume
          </h2>

          <div className="space-y-8">
            {/* File upload */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                1. Upload Your Resume
              </label>
              <FileUpload file={file} onFileSelect={setFile} />
            </div>

            {/* Input mode selector */}
            <div>
              <label className="mb-3 block text-sm font-medium text-gray-700">
                2. Choose Analysis Mode
              </label>
              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  {
                    mode: "jd" as InputMode,
                    label: "Paste Job Description",
                    desc: "Full ATS analysis",
                    icon: FileText,
                  },
                  {
                    mode: "linkedin" as InputMode,
                    label: "LinkedIn URL",
                    desc: "Import from LinkedIn",
                    icon: Link2,
                  },
                  {
                    mode: "none" as InputMode,
                    label: "No Job Description",
                    desc: "Resume strength check",
                    icon: Target,
                  },
                ].map((opt) => (
                  <button
                    key={opt.mode}
                    type="button"
                    onClick={() => setInputMode(opt.mode)}
                    className={`flex items-center gap-3 rounded-lg border-2 px-4 py-3 text-left transition-all ${
                      inputMode === opt.mode
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <opt.icon
                      className={`h-5 w-5 flex-shrink-0 ${
                        inputMode === opt.mode
                          ? "text-primary-600"
                          : "text-gray-400"
                      }`}
                    />
                    <div>
                      <p
                        className={`text-sm font-medium ${
                          inputMode === opt.mode
                            ? "text-primary-700"
                            : "text-gray-700"
                        }`}
                      >
                        {opt.label}
                      </p>
                      <p className="text-xs text-gray-500">{opt.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Job description input */}
            {inputMode === "jd" && (
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  3. Paste the Job Description
                </label>
                <JobDescriptionInput
                  value={jobDescription}
                  onChange={setJobDescription}
                />
              </div>
            )}

            {/* LinkedIn URL input (Feature 10) */}
            {inputMode === "linkedin" && (
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  3. Paste LinkedIn Job URL
                </label>
                <input
                  type="url"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  placeholder="https://www.linkedin.com/jobs/view/..."
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Note: LinkedIn may block automated access. If import fails,
                  use the &quot;Paste Job Description&quot; mode instead.
                </p>
              </div>
            )}

            {inputMode === "none" && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
                Resume Strength mode evaluates your resume without a specific 
                job description. It checks technical skill diversity, bullet 
                quality, structure, and quantified achievements.
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !canSubmit()}
              className="btn-primary w-full"
            >
              {isAnalyzing
                ? "Analyzing..."
                : inputMode === "none"
                ? "Analyze Resume Strength"
                : "Analyze Resume"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
