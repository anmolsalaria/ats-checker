"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import JobDescriptionInput from "@/components/JobDescriptionInput";
import AnalysisAnimation from "@/components/AnalysisAnimation";
import { analyzeResume, analyzeResumeFileOnly, ApiError } from "@/lib/api";
import { AnalysisResult, ResumeStrengthResult } from "@/types";
import { FileText, Zap, Target, TrendingUp } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skipJD, setSkipJD] = useState(false);

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload a resume.");
      return;
    }

    if (!skipJD && jobDescription.trim().length < 50) {
      setError("Job description must be at least 50 characters, or toggle the no-JD mode.");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    // Show animation for at least 2.5 s
    const animStart = Date.now();

    try {
      let resultData: AnalysisResult | ResumeStrengthResult;

      if (skipJD) {
        resultData = await analyzeResumeFileOnly(file);
        const elapsed = Date.now() - animStart;
        if (elapsed < 2500) await new Promise((r) => setTimeout(r, 2500 - elapsed));
        sessionStorage.setItem("strengthResult", JSON.stringify(resultData));
        sessionStorage.removeItem("analysisResult");
        router.push("/results");
      } else {
        resultData = await analyzeResume(file, jobDescription);
        const elapsed = Date.now() - animStart;
        if (elapsed < 2500) await new Promise((r) => setTimeout(r, 2500 - elapsed));
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

  return (
    <div className="page-transition">
      {/* Animated overlay (Feature 7) */}
      <AnalysisAnimation isActive={isAnalyzing} />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 py-20 text-white">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
            AI ATS Resume Analyzer
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-primary-100">
            Optimize your resume for Applicant Tracking Systems. Get instant
            feedback on keyword matching, skill gaps, and actionable suggestions.
          </p>
        </div>
      </section>

      {/* Feature cards */}
      <section className="mx-auto -mt-10 max-w-5xl px-4">
        <div className="grid gap-4 sm:grid-cols-4">
          {[
            { icon: FileText, title: "Upload Resume", desc: "PDF or DOCX supported" },
            { icon: Target, title: "ATS Score", desc: "Weighted 4-factor model" },
            { icon: Zap, title: "Keyword Match", desc: "Curated skill dictionary" },
            { icon: TrendingUp, title: "Suggestions", desc: "Actionable improvements" },
          ].map((f) => (
            <div key={f.title} className="card flex flex-col items-center text-center">
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

            {/* No-JD toggle (Feature 6) */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setSkipJD(!skipJD)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                  skipJD ? "bg-primary-600" : "bg-gray-200"
                }`}
              >
                <span
                  className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${
                    skipJD ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
              <span className="text-sm text-gray-700">
                Analyze without a job description (Resume Strength mode)
              </span>
            </div>

            {/* Job description (hidden when skipJD) */}
            {!skipJD && (
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  2. Paste the Job Description
                </label>
                <JobDescriptionInput
                  value={jobDescription}
                  onChange={setJobDescription}
                />
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
              disabled={isAnalyzing || !file || (!skipJD && !jobDescription.trim())}
              className="btn-primary w-full"
            >
              {isAnalyzing ? "Analyzing..." : skipJD ? "Analyze Resume Strength" : "Analyze Resume"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
