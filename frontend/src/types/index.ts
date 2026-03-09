/** API response and request types -- v3. */

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

export interface BulletAnalysisItem {
  text: string;
  has_action_verb: boolean;
  action_verb: string | null;
  is_weak_verb: boolean;
  has_technology: boolean;
  technologies: string[];
  has_metric: boolean;
  metrics: string[];
  score: number;
  suggestion: string | null;
}

/** Response from /analyze and /analyze-text */
export interface AnalysisResult {
  ats_score: number;
  ats_grade: string;
  keyword_match_score: number;
  semantic_similarity_score: number;
  skill_coverage_score: number;
  bullet_quality_score: number;
  structure_score: number;
  detected_role: string;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
  resume_sections: ResumeSections;
  skill_gap: Record<string, CategorySkillGap>;
  bullet_analysis: BulletAnalysisItem[];
}

/** Response from /analyze-resume-only (Feature 8) */
export interface ResumeStrengthResult {
  resume_strength_score: number;
  tech_coverage_score: number;
  structure_score: number;
  impact_score: number;
  bullet_quality_score: number;
  matched_skills: string[];
  missing_skills: string[];
  categorised_skills: Record<string, string[]>;
  resume_sections: ResumeSections;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  bullet_analysis: BulletAnalysisItem[];
}

export interface HealthStatus {
  status: string;
  version: string;
}
