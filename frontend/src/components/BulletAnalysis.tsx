"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { BulletAnalysisItem } from "@/types";

interface BulletAnalysisProps {
  bullets: BulletAnalysisItem[];
}

function getBulletColor(score: number) {
  if (score >= 70) return { bg: "bg-green-50", border: "border-green-200", text: "text-green-700" };
  if (score >= 40) return { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700" };
  return { bg: "bg-red-50", border: "border-red-200", text: "text-red-700" };
}

export default function BulletAnalysis({ bullets }: BulletAnalysisProps) {
  if (bullets.length === 0) {
    return (
      <p className="text-sm italic text-gray-400">
        No bullet points detected in the resume.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {bullets.slice(0, 10).map((bullet, idx) => {
        const colors = getBulletColor(bullet.score);
        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`rounded-lg border ${colors.border} ${colors.bg} p-4`}
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm text-gray-800 leading-relaxed flex-1">
                &ldquo;{bullet.text.length > 120 ? bullet.text.slice(0, 120) + "..." : bullet.text}&rdquo;
              </p>
              <span
                className={`flex-shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${colors.text}`}
              >
                {bullet.score}%
              </span>
            </div>

            {/* Indicators */}
            <div className="mt-2 flex flex-wrap gap-2">
              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
                bullet.has_action_verb ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
              }`}>
                {bullet.has_action_verb ? (
                  <CheckCircle2 className="h-3 w-3" />
                ) : (
                  <XCircle className="h-3 w-3" />
                )}
                Action Verb{bullet.action_verb ? `: ${bullet.action_verb}` : ""}
              </span>

              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
                bullet.has_technology ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-500"
              }`}>
                {bullet.has_technology ? (
                  <CheckCircle2 className="h-3 w-3" />
                ) : (
                  <XCircle className="h-3 w-3" />
                )}
                Technology
              </span>

              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
                bullet.has_metric ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-500"
              }`}>
                {bullet.has_metric ? (
                  <CheckCircle2 className="h-3 w-3" />
                ) : (
                  <XCircle className="h-3 w-3" />
                )}
                Metrics
              </span>

              {bullet.is_weak_verb && (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700">
                  <AlertTriangle className="h-3 w-3" />
                  Weak Verb
                </span>
              )}
            </div>

            {/* Suggestion */}
            {bullet.suggestion && (
              <p className="mt-2 text-xs text-gray-600 italic">
                Tip: {bullet.suggestion}
              </p>
            )}
          </motion.div>
        );
      })}
      {bullets.length > 10 && (
        <p className="text-center text-xs text-gray-400">
          Showing 10 of {bullets.length} bullet points
        </p>
      )}
    </div>
  );
}
