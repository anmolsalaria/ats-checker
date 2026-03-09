"use client";

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export default function JobDescriptionInput({
  value,
  onChange,
}: JobDescriptionInputProps) {
  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste the full job description here. Include the role title, responsibilities, required skills, and qualifications for the best analysis..."
        rows={8}
        className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
      />
      <p className="mt-1 text-right text-xs text-gray-400">
        {value.length} characters
        {value.length > 0 && value.length < 50 && (
          <span className="text-amber-500"> (minimum 50)</span>
        )}
      </p>
    </div>
  );
}
