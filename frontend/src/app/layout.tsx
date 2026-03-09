import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI ATS Resume Analyzer",
  description:
    "Optimize your resume for Applicant Tracking Systems with AI-powered analysis, keyword matching, and improvement suggestions.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        <main className="min-h-[calc(100vh-4rem)]">{children}</main>
        <footer className="border-t border-gray-200 bg-white py-6 text-center text-sm text-gray-500">
          <p>
            &copy; {new Date().getFullYear()} AI ATS Resume Analyzer. Built for
            job seekers.
          </p>
        </footer>
      </body>
    </html>
  );
}
