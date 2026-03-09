"use client";

import clsx from "clsx";

interface KeywordListProps {
  keywords: string[];
  variant: "matched" | "missing";
}

export default function KeywordList({ keywords, variant }: KeywordListProps) {
  if (keywords.length === 0) {
    return (
      <p className="text-sm italic text-gray-400">
        {variant === "matched"
          ? "No matched keywords found."
          : "No missing keywords — great job!"}
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {keywords.map((keyword) => (
        <span
          key={keyword}
          className={clsx(
            "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
            variant === "matched"
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          )}
        >
          {keyword}
        </span>
      ))}
    </div>
  );
}
