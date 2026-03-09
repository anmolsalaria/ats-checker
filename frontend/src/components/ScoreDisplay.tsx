"use client";

import { buildStyles, CircularProgressbar } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

interface ScoreDisplayProps {
  label: string;
  score: number;
  size?: "sm" | "md" | "lg";
}

function getScoreColor(score: number): string {
  if (score >= 75) return "#16a34a"; // green-600
  if (score >= 50) return "#f59e0b"; // amber-500
  return "#ef4444"; // red-500
}

function getScoreLabel(score: number): string {
  if (score >= 80) return "Excellent";
  if (score >= 60) return "Good";
  if (score >= 40) return "Fair";
  return "Needs Work";
}

export default function ScoreDisplay({
  label,
  score,
  size = "md",
}: ScoreDisplayProps) {
  const color = getScoreColor(score);
  const dimensions = {
    sm: "h-20 w-20",
    md: "h-28 w-28",
    lg: "h-36 w-36",
  };

  return (
    <div className="card flex flex-col items-center justify-center py-8">
      <div className={dimensions[size]}>
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
