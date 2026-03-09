"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Step {
  label: string;
  icon: React.ReactNode;
}

const STEPS: Step[] = [
  {
    label: "Uploading Resume",
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    label: "Extracting Keywords",
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
      </svg>
    ),
  },
  {
    label: "Running AI Analysis",
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    label: "Generating Score",
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
];

interface AnalysisAnimationProps {
  /** Whether the animation should be visible */
  isActive: boolean;
}

export default function AnalysisAnimation({ isActive }: AnalysisAnimationProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isActive) {
      setCurrentStep(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 700);

    return () => clearInterval(interval);
  }, [isActive]);

  if (!isActive) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/70 backdrop-blur-sm"
    >
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
        className="mx-4 w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl"
      >
        {/* Scanning effect */}
        <div className="relative mb-8 flex justify-center">
          <motion.div
            className="absolute inset-0 rounded-full bg-primary-400/20"
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="relative z-10 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-lg"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          >
            <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </motion.div>
        </div>

        <h3 className="mb-6 text-center text-lg font-semibold text-gray-900">
          Analyzing Your Resume
        </h3>

        {/* Progress steps */}
        <div className="space-y-3">
          {STEPS.map((step, idx) => {
            const isComplete = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <motion.div
                key={step.label}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: idx * 0.15 }}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                  isComplete
                    ? "bg-green-50 text-green-700"
                    : isCurrent
                    ? "bg-primary-50 text-primary-700"
                    : "bg-gray-50 text-gray-400"
                }`}
              >
                {/* Status icon */}
                <div className="flex-shrink-0">
                  {isComplete ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 500 }}
                    >
                      <svg className="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </motion.div>
                  ) : isCurrent ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-6 w-6 rounded-full border-2 border-primary-300 border-t-primary-600"
                    />
                  ) : (
                    <div className="h-6 w-6 rounded-full border-2 border-gray-200" />
                  )}
                </div>

                {/* Label */}
                <span className={`text-sm font-medium ${isCurrent ? "animate-pulse" : ""}`}>
                  {step.label}
                </span>
              </motion.div>
            );
          })}
        </div>

        {/* Overall progress bar */}
        <div className="mt-6">
          <div className="h-2 overflow-hidden rounded-full bg-gray-200">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-600"
              initial={{ width: "0%" }}
              animate={{
                width: `${((currentStep + 1) / STEPS.length) * 100}%`,
              }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          <p className="mt-2 text-center text-xs text-gray-500">
            Step {currentStep + 1} of {STEPS.length}
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
