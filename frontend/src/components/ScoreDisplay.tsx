"use client";

import { buildStyles, CircularProgressbar } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

interface ScoreDisplayProps {
  label: string;
  score: number;
  size?: "sm" | "md" | "lg";
  grade?: string;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "#16a34a"; // green-600
  if (score >= 60) return "#f59e0b"; // amber-500
  if (score >= 40) return "#f97316"; // orange-500
  return "#ef4444"; // red-500
}

function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Very Good";
  if (score >= 70) return "Good";
  if (score >= 60) return "Fair";
  if (score >= 40) return "Needs Work";
  return "Poor";
}

function getGradeColor(grade: string): string {
  switch (grade) {
    case "A":
      return "#16a34a";
    case "B":
      return "#22c55e";
    case "C":
      return "#f59e0b";
    case "D":
      return "#f97316";
    default:
      return "#ef4444";
  }
}

export default function ScoreDisplay({
  label,
  score,
  size = "md",
  grade,
}: ScoreDisplayProps) {
  const color = getScoreColor(score);
  const dimensions = {
    sm: "h-20 w-20",
    md: "h-28 w-28",
    lg: "h-36 w-36",
  };

  return (
    <div className="card flex flex-col items-center justify-center py-8">
      <div className={`relative ${dimensions[size]}`}>
        <CircularProgressbar
          value={score}
          text={`${score}%`}
          styles={buildStyles({
            textSize: "1.5rem",
            pathColor: color,
            textColor: color,
            trailColor: "#e5e7eb",
            pathTransitionDuration: 1,
          })}
        />
        {/* ATS Grade badge (Feature 9) */}
        {grade && size === "lg" && (
          <div
            className="absolute -right-2 -top-2 flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white shadow-lg"
            style={{ backgroundColor: getGradeColor(grade) }}
          >
            {grade}
          </div>
        )}
      </div>
      <p className="mt-3 text-sm font-medium text-gray-600">{label}</p>
      {size === "lg" && (
        <span
          className="mt-1 rounded-full px-3 py-0.5 text-xs font-semibold"
          style={{
            color,
            backgroundColor: `${color}15`,
          }}
        >
          {getScoreLabel(score)}
        </span>
      )}
    </div>
  );
}
