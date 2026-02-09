import { ATSAnalysisResponse, OptimizeResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeResume(
  resumeText: string,
  jdText: string,
  resumeFile?: File,
  includeLlm: boolean = true
): Promise<ATSAnalysisResponse> {
  const formData = new FormData();
  formData.append("jd_text", jdText);
  formData.append("include_llm_analysis", String(includeLlm));

  if (resumeFile) {
    formData.append("resume_file", resumeFile);
  } else {
    formData.append("resume_text", resumeText);
  }

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
  jdText: string,
  resumeFile?: File
): Promise<OptimizeResponse> {
  const formData = new FormData();
  formData.append("jd_text", jdText);

  if (resumeFile) {
    formData.append("resume_file", resumeFile);
  } else {
    formData.append("resume_text", resumeText);
  }

  const response = await fetch(`${API_URL}/api/v1/optimize`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Optimization failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getHistory(): Promise<Array<Record<string, unknown>>> {
  const response = await fetch(`${API_URL}/api/v1/history`);
  if (!response.ok) throw new Error("Failed to fetch history");
  return response.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/api/v1/health`);
  return response.json();
}
