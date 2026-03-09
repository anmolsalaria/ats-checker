"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import JobDescriptionInput from "@/components/JobDescriptionInput";
import { analyzeResume, ApiError } from "@/lib/api";
import { AnalysisResult } from "@/types";
import { FileText, Zap, Target, TrendingUp } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!file || !jobDescription.trim()) {
      setError("Please upload a resume and enter a job description.");
      return;
    }

    if (jobDescription.trim().length < 50) {
      setError("Job description must be at least 50 characters.");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result: AnalysisResult = await analyzeResume(file, jobDescription);

      // Store result in sessionStorage for the results page
      sessionStorage.setItem("analysisResult", JSON.stringify(result));
      router.push("/results");
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

  return (
    <div className="page-transition">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 py-20 text-white">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
            AI ATS Resume Analyzer
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-primary-100">
            Optimize your resume for Applicant Tracking Systems. Get instant
            feedback on keyword matching, ATS compatibility score, and
            actionable improvement suggestions.
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto -mt-10 max-w-5xl px-4">
        <div className="grid gap-4 sm:grid-cols-4">
          {[
            {
              icon: FileText,
              title: "Upload Resume",
              desc: "PDF or DOCX supported",
            },
            {
              icon: Target,
              title: "ATS Score",
              desc: "Instant compatibility check",
            },
            {
              icon: Zap,
              title: "Keyword Match",
              desc: "Find missing skills",
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

      {/* Analysis Form */}
      <section className="mx-auto max-w-4xl px-4 py-16">
        <div className="card">
          <h2 className="mb-6 text-2xl font-bold text-gray-900">
            Analyze Your Resume
          </h2>

          <div className="space-y-8">
            {/* File Upload */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                1. Upload Your Resume
              </label>
              <FileUpload file={file} onFileSelect={setFile} />
            </div>

            {/* Job Description */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                2. Paste the Job Description
              </label>
              <JobDescriptionInput
                value={jobDescription}
                onChange={setJobDescription}
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !file || !jobDescription.trim()}
              className="btn-primary w-full"
            >
              {isAnalyzing ? (
                <span className="flex items-center gap-2">
                  <svg
                    className="h-5 w-5 animate-spin"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                "Analyze Resume"
              )}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
