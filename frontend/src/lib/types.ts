export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  linkedin: string;
  github: string;
  location: string;
  portfolio: string;
}

export interface ExperienceEntry {
  company: string;
  role: string;
  dates: string;
  location: string;
  bullets: string[];
}

export interface EducationEntry {
  school: string;
  degree: string;
  dates: string;
  gpa: string;
  details: string[];
}

export interface ProjectEntry {
  name: string;
  description: string;
  tech_used: string[];
  bullets: string[];
}

export interface ParsedResume {
  raw_text: string;
  raw_latex: string | null;
  input_format: string;
  contact: ContactInfo;
  sections: Record<string, string>;
  latex_sections: Record<string, string> | null;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: string[];
  word_count: number;
  estimated_pages: number;
}

export interface KeywordWithWeight {
  keyword: string;
  weight: number;
  category: string;
}

export interface ParsedJD {
  raw_text: string;
  title: string;
  company: string | null;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  qualifications: string[];
  experience_level: string;
  keywords: KeywordWithWeight[];
}

export interface KeywordMatchResult {
  keyword: string;
  category: string;
  found: boolean;
  match_type: string;
  match_score: number;
  matched_text: string | null;
  location_in_resume: string | null;
}

export interface SemanticResult {
  overall_similarity: number;
  skills_similarity: number;
  experience_similarity: number;
  education_similarity: number;
  section_similarities: Record<string, number>;
}

export interface StructureDetails {
  has_name: boolean;
  has_email: boolean;
  has_phone: boolean;
  has_linkedin: boolean;
  has_github: boolean;
  has_summary: boolean;
  has_experience: boolean;
  has_education: boolean;
  has_skills: boolean;
  has_projects: boolean;
  word_count: number;
  estimated_pages: number;
  has_consistent_dates: boolean;
  has_standard_headers: boolean;
  formatting_issues: string[];
}

export interface StructureResult {
  contact_score: number;
  sections_score: number;
  length_score: number;
  formatting_score: number;
  total_score: number;
  details: StructureDetails;
}

export interface LLMAnalysis {
  qualitative_fit: string;
  fit_explanation: string;
  strengths: string[];
  gaps: string[];
  bullet_rewrites: Array<{
    original: string;
    improved: string;
    reason: string;
  }>;
  missing_keywords_to_add: Array<{
    keyword: string;
    where: string;
    how: string;
  }>;
  skills_section_rewrite: string;
  interview_readiness: number;
  interview_topics: string[];
  overall_recommendation: string;
}

export interface Suggestion {
  priority: string;
  category: string;
  title: string;
  description: string;
  estimated_impact: number;
}

export interface ATSAnalysisResponse {
  overall_score: number;
  keyword_score: number;
  semantic_score: number;
  structure_score: number;
  recruiter_status: string;
  rank_estimate: string;
  keyword_results: KeywordMatchResult[];
  semantic_results: SemanticResult;
  structure_results: StructureResult;
  parsed_resume: ParsedResume;
  parsed_jd: ParsedJD;
  llm_analysis: LLMAnalysis | null;
  suggestions: Suggestion[];
  analysis_id: string;
  analyzed_at: string;
}

export interface BulletChange {
  section: string;
  entry_index: number;
  bullet_index: number;
  original: string;
  optimized: string;
  keywords_added: string[];
  reason: string;
  accepted: boolean;
}

export interface ResumeChange {
  section: string;
  change_type: string;
  original: string;
  optimized: string;
  original_latex: string | null;
  optimized_latex: string | null;
  line_number: number | null;
  keywords_added: string[];
  reason: string;
  accepted: boolean;
}

export interface OptimizeResponse {
  input_format: string;
  original_text: string;
  optimized_text: string;
  original_latex: string | null;
  optimized_latex: string | null;
  original_score: number;
  optimized_score: number;
  score_delta: number;
  changes: ResumeChange[];
  validation: {
    valid: boolean;
    fabricated_skills: string[];
    message: string;
  };
  latex_validation: {
    valid: boolean;
    errors: string[];
  } | null;
  fabricated_skills_removed: string[];
  keywords_added: string[];
  keywords_impossible: Array<{ keyword: string; reason: string }>;
  optimized_summary: string;
  optimized_skills: string;
  optimized_bullets: BulletChange[];
}
