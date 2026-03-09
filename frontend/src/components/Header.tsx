"use client";

import Link from "next/link";
import { FileSearch } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <FileSearch className="h-7 w-7 text-primary-600" />
          <span className="text-lg font-bold text-gray-900">
            ATS Analyzer
          </span>
        </Link>
        <nav className="flex items-center gap-4">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}
