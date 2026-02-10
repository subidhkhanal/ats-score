"use client";

import { useState, useCallback } from "react";
import { ATSAnalysisResponse, OptimizeResponse } from "@/lib/types";
import { analyzeResume, optimizeResume } from "@/lib/api";

export function useAnalysis() {
  const [analysis, setAnalysis] = useState<ATSAnalysisResponse | null>(null);
  const [optimization, setOptimization] = useState<OptimizeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(
    async (resumeText: string, jdText: string) => {
      setLoading(true);
      setError(null);
      setAnalysis(null);
      setOptimization(null);
      try {
        const result = await analyzeResume(resumeText, jdText);
        setAnalysis(result);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Analysis failed";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const optimize = useCallback(
    async (resumeText: string, jdText: string) => {
      setOptimizing(true);
      setError(null);
      try {
        const result = await optimizeResume(resumeText, jdText);
        setOptimization(result);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Optimization failed";
        setError(message);
        return null;
      } finally {
        setOptimizing(false);
      }
    },
    []
  );

  return {
    analysis,
    optimization,
    loading,
    optimizing,
    error,
    analyze,
    optimize,
    setAnalysis,
    setOptimization,
  };
}
