"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnalysisResult } from "@/types";
import ScoreDisplay from "@/components/ScoreDisplay";
import KeywordList from "@/components/KeywordList";
import Suggestions from "@/components/Suggestions";
import {
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  XCircle,
  Lightbulb,
  Layers,
} from "lucide-react";

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("analysisResult");
    if (stored) {
      setResult(JSON.parse(stored));
    } else {
      router.push("/");
    }
  }, [router]);

  if (!result) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  const sectionEntries = Object.entries(result.resume_sections);

  return (
    <div className="page-transition mx-auto max-w-6xl px-4 py-10">
      {/* Back button */}
      <button
        onClick={() => router.push("/")}
        className="btn-secondary mb-8 gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        Analyze Another Resume
      </button>

      {/* Score Overview */}
      <div className="mb-8 grid gap-6 lg:grid-cols-3">
        <ScoreDisplay
          label="Overall ATS Score"
          score={result.ats_score}
          size="lg"
        />
        <ScoreDisplay
          label="Keyword Match"
          score={result.keyword_match_score}
          size="md"
        />
        <ScoreDisplay
          label="Semantic Similarity"
          score={result.semantic_similarity_score}
          size="md"
        />
      </div>

      {/* Keywords & Suggestions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Matched Keywords */}
        <div className="card">
          <div className="mb-4 flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Matched Keywords
            </h3>
            <span className="ml-auto rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
              {result.matched_keywords.length}
            </span>
          </div>
          <KeywordList keywords={result.matched_keywords} variant="matched" />
        </div>

        {/* Missing Keywords */}
        <div className="card">
          <div className="mb-4 flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-900">
              Missing Keywords
            </h3>
            <span className="ml-auto rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700">
              {result.missing_keywords.length}
            </span>
          </div>
          <KeywordList keywords={result.missing_keywords} variant="missing" />
        </div>
      </div>

      {/* Skill Gap Analysis */}
      {result.skill_gap_analysis && (
        <div className="mt-6 card">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Skill Gap Analysis
            </h3>
          </div>
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <h4 className="mb-2 text-sm font-medium text-gray-600">
                Technical Skills
              </h4>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="h-3 overflow-hidden rounded-full bg-gray-200">
                    <div
                      className="h-full rounded-full bg-primary-600 transition-all duration-700"
                      style={{
                        width: `${
                          result.skill_gap_analysis.technical.matched +
                            result.skill_gap_analysis.technical.missing >
                          0
                            ? (result.skill_gap_analysis.technical.matched /
                                (result.skill_gap_analysis.technical.matched +
                                  result.skill_gap_analysis.technical.missing)) *
                              100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-600">
                  {result.skill_gap_analysis.technical.matched}/
                  {result.skill_gap_analysis.technical.matched +
                    result.skill_gap_analysis.technical.missing}
                </span>
              </div>
              {result.skill_gap_analysis.technical.keywords.length > 0 && (
                <p className="mt-2 text-xs text-gray-500">
                  Missing:{" "}
                  {result.skill_gap_analysis.technical.keywords.join(", ")}
                </p>
              )}
            </div>
            <div>
              <h4 className="mb-2 text-sm font-medium text-gray-600">
                Soft Skills
              </h4>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="h-3 overflow-hidden rounded-full bg-gray-200">
                    <div
                      className="h-full rounded-full bg-indigo-500 transition-all duration-700"
                      style={{
                        width: `${
                          result.skill_gap_analysis.soft_skills.matched +
                            result.skill_gap_analysis.soft_skills.missing >
                          0
                            ? (result.skill_gap_analysis.soft_skills.matched /
                                (result.skill_gap_analysis.soft_skills.matched +
                                  result.skill_gap_analysis.soft_skills
                                    .missing)) *
                              100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-600">
                  {result.skill_gap_analysis.soft_skills.matched}/
                  {result.skill_gap_analysis.soft_skills.matched +
                    result.skill_gap_analysis.soft_skills.missing}
                </span>
              </div>
              {result.skill_gap_analysis.soft_skills.keywords.length > 0 && (
                <p className="mt-2 text-xs text-gray-500">
                  Missing:{" "}
                  {result.skill_gap_analysis.soft_skills.keywords.join(", ")}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Resume Sections */}
      <div className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Resume Sections Detected
          </h3>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {sectionEntries.map(([section, detected]) => (
            <div
              key={section}
              className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
                detected
                  ? "border-green-200 bg-green-50 text-green-700"
                  : "border-gray-200 bg-gray-50 text-gray-400"
              }`}
            >
              {detected ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <span className="capitalize">{section}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold text-gray-900">
            Improvement Suggestions
          </h3>
        </div>
        <Suggestions suggestions={result.suggestions} />
      </div>
    </div>
  );
}
