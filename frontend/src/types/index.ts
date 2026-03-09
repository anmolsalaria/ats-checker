/** API response and request types — v2. */

export interface CategorySkillGap {
  matched: number;
  required: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface ResumeSections {
  experience: boolean;
  education: boolean;
  skills: boolean;
  projects: boolean;
  certifications: boolean;
  summary: boolean;
}

/** Response from /analyze and /analyze-text */
export interface AnalysisResult {
  ats_score: number;
  keyword_match_score: number;
  semantic_similarity_score: number;
  skill_coverage_score: number;
  structure_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
  resume_sections: ResumeSections;
  skill_gap: Record<string, CategorySkillGap>;
}

/** Response from /analyze-resume-only (Feature 6) */
export interface ResumeStrengthResult {
  resume_strength_score: number;
  tech_coverage_score: number;
  structure_score: number;
  impact_score: number;
  matched_skills: string[];
  missing_skills: string[];
  categorised_skills: Record<string, string[]>;
  resume_sections: ResumeSections;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

export interface HealthStatus {
  status: string;
  version: string;
}
