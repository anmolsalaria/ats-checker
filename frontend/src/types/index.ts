/** API response and request types. */

export interface SkillGap {
  matched: number;
  missing: number;
  keywords: string[];
}

export interface SkillGapAnalysis {
  technical: SkillGap;
  soft_skills: SkillGap;
}

export interface ResumeSections {
  experience: boolean;
  education: boolean;
  skills: boolean;
  projects: boolean;
  certifications: boolean;
  summary: boolean;
}

export interface AnalysisResult {
  ats_score: number;
  keyword_match_score: number;
  semantic_similarity_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
  resume_sections: ResumeSections;
  skill_gap_analysis: SkillGapAnalysis | null;
}

export interface HealthStatus {
  status: string;
  version: string;
}
