"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { AnalysisResult, ResumeStrengthResult } from "@/types";
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
  TrendingUp,
  TrendingDown,
} from "lucide-react";

/* ---------- shared fade-in helper ---------- */
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08 },
  }),
};

/* ========================================================================== */
/*  ATS Analysis Results (with JD)                                            */
/* ========================================================================== */
function ATSResults({ result }: { result: AnalysisResult }) {
  const sectionEntries = Object.entries(result.resume_sections);
  const skillGapEntries = Object.entries(result.skill_gap || {}).filter(
    ([, v]) => v.required > 0 || v.matched > 0,
  );

  return (
    <>
      {/* Score overview */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        custom={0}
        className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        <ScoreDisplay label="Overall ATS Score" score={result.ats_score} size="lg" />
        <ScoreDisplay label="Keyword Match" score={result.keyword_match_score} size="md" />
        <ScoreDisplay label="Semantic Similarity" score={result.semantic_similarity_score} size="md" />
        <ScoreDisplay label="Skill Coverage" score={result.skill_coverage_score} size="md" />
      </motion.div>

      {/* Keywords */}
      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={1} className="card">
          <div className="mb-4 flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Matched Keywords</h3>
            <span className="ml-auto rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
              {result.matched_keywords.length}
            </span>
          </div>
          <KeywordList keywords={result.matched_keywords} variant="matched" />
        </motion.div>

        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={2} className="card">
          <div className="mb-4 flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-900">Missing Keywords</h3>
            <span className="ml-auto rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700">
              {result.missing_keywords.length}
            </span>
          </div>
          <KeywordList keywords={result.missing_keywords} variant="missing" />
        </motion.div>
      </div>

      {/* Categorised skill gap (Feature 5) */}
      {skillGapEntries.length > 0 && (
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={3} className="mt-6 card">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Skill Gap by Category</h3>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {skillGapEntries.map(([cat, info]) => {
              const total = info.matched + (info.missing_skills?.length || 0);
              const pct = total > 0 ? (info.matched / total) * 100 : 0;
              return (
                <div key={cat} className="rounded-lg border border-gray-100 bg-gray-50 p-4">
                  <h4 className="mb-2 text-sm font-semibold capitalize text-gray-700">
                    {cat.replace(/_/g, " ")}
                  </h4>
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="h-2.5 overflow-hidden rounded-full bg-gray-200">
                        <motion.div
                          className="h-full rounded-full bg-primary-600"
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                    <span className="text-xs font-medium text-gray-600">
                      {info.matched}/{total}
                    </span>
                  </div>
                  {info.missing_skills?.length > 0 && (
                    <p className="mt-2 text-xs text-gray-500">
                      Missing: {info.missing_skills.join(", ")}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Resume sections */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={4} className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Resume Sections</h3>
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
              {detected ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              <span className="capitalize">{section}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Suggestions */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={5} className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold text-gray-900">Suggestions</h3>
        </div>
        <Suggestions suggestions={result.suggestions} />
      </motion.div>
    </>
  );
}

/* ========================================================================== */
/*  Resume Strength Results (no JD — Feature 6)                               */
/* ========================================================================== */
function StrengthResults({ result }: { result: ResumeStrengthResult }) {
  const sectionEntries = Object.entries(result.resume_sections);

  return (
    <>
      {/* Score overview */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        custom={0}
        className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        <ScoreDisplay label="Resume Strength" score={result.resume_strength_score} size="lg" />
        <ScoreDisplay label="Tech Coverage" score={result.tech_coverage_score} size="md" />
        <ScoreDisplay label="Structure" score={result.structure_score} size="md" />
        <ScoreDisplay label="Impact Statements" score={result.impact_score} size="md" />
      </motion.div>

      {/* Strengths & Weaknesses */}
      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={1} className="card">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Strengths</h3>
          </div>
          <ul className="space-y-2">
            {result.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-500" />
                {s}
              </li>
            ))}
            {result.strengths.length === 0 && (
              <li className="text-sm text-gray-400">No notable strengths detected.</li>
            )}
          </ul>
        </motion.div>

        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={2} className="card">
          <div className="mb-4 flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-900">Weaknesses</h3>
          </div>
          <ul className="space-y-2">
            {result.weaknesses.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <XCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-400" />
                {w}
              </li>
            ))}
            {result.weaknesses.length === 0 && (
              <li className="text-sm text-gray-400">No weaknesses found — great job!</li>
            )}
          </ul>
        </motion.div>
      </div>

      {/* Detected skills by category */}
      {Object.keys(result.categorised_skills).length > 0 && (
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={3} className="mt-6 card">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Skills Detected</h3>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(result.categorised_skills).map(([cat, skills]) => (
              <div key={cat} className="rounded-lg border border-gray-100 bg-gray-50 p-4">
                <h4 className="mb-2 text-sm font-semibold capitalize text-gray-700">
                  {cat.replace(/_/g, " ")}
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {skills.map((s) => (
                    <span
                      key={s}
                      className="rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-700"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Resume sections */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={4} className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Resume Sections</h3>
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
              {detected ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              <span className="capitalize">{section}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Suggestions */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={5} className="mt-6 card">
        <div className="mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold text-gray-900">Suggestions</h3>
        </div>
        <Suggestions suggestions={result.suggestions} />
      </motion.div>
    </>
  );
}

/* ========================================================================== */
/*  Page                                                                      */
/* ========================================================================== */
export default function ResultsPage() {
  const router = useRouter();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [strengthResult, setStrengthResult] = useState<ResumeStrengthResult | null>(null);

  useEffect(() => {
    const a = sessionStorage.getItem("analysisResult");
    const s = sessionStorage.getItem("strengthResult");
    if (a) {
      setAnalysisResult(JSON.parse(a));
    } else if (s) {
      setStrengthResult(JSON.parse(s));
    } else {
      router.push("/");
    }
  }, [router]);

  if (!analysisResult && !strengthResult) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <button onClick={() => router.push("/")} className="btn-secondary mb-8 gap-2">
        <ArrowLeft className="h-4 w-4" />
        Analyze Another Resume
      </button>

      {analysisResult ? (
        <ATSResults result={analysisResult} />
      ) : strengthResult ? (
        <StrengthResults result={strengthResult} />
      ) : null}
    </div>
  );
}
