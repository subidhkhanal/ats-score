import { ATSAnalysisResponse, OptimizeResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeResume(
  resumeText: string,
  jdText: string,
  includeLlm: boolean = true
): Promise<ATSAnalysisResponse> {
  const formData = new FormData();
  formData.append("resume_text", resumeText);
  formData.append("jd_text", jdText);
  formData.append("include_llm_analysis", String(includeLlm));

  const response = await fetch(`${API_URL}/api/v1/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
}

export async function optimizeResume(
  resumeText: string,
  jdText: string
): Promise<OptimizeResponse> {
  const formData = new FormData();
  formData.append("resume_text", resumeText);
  formData.append("jd_text", jdText);

  const response = await fetch(`${API_URL}/api/v1/optimize`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Optimization failed: ${response.statusText}`);
  }

  return response.json();
}
