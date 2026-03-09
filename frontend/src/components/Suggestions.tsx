"use client";

import { ChevronRight } from "lucide-react";

interface SuggestionsProps {
  suggestions: string[];
}

export default function Suggestions({ suggestions }: SuggestionsProps) {
  if (suggestions.length === 0) {
    return (
      <p className="text-sm italic text-gray-400">
        No suggestions — your resume looks great!
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {suggestions.map((suggestion, index) => (
        <li
          key={index}
          className="flex gap-3 rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700"
        >
          <ChevronRight className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-500" />
          <span>{suggestion}</span>
        </li>
      ))}
    </ul>
  );
}
