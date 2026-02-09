"use client";

import { LLMAnalysis, Suggestion } from "@/lib/types";

interface AIRecommendationsProps {
  llmAnalysis: LLMAnalysis | null;
  suggestions: Suggestion[];
}

export default function AIRecommendations({
  llmAnalysis,
  suggestions,
}: AIRecommendationsProps) {
  if (!llmAnalysis && suggestions.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-center">
        <p className="text-sm text-muted-foreground">
          AI analysis is unavailable. Set up your Gemini API key to get
          AI-powered recommendations.
        </p>
      </div>
    );
  }

  const priorityColor = (p: string) => {
    switch (p) {
      case "high":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "medium":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "low":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {llmAnalysis && (
        <>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
              AI Fit Assessment
            </h3>
            <div className="rounded-lg bg-secondary/30 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${
                    llmAnalysis.qualitative_fit === "strong_match"
                      ? "bg-green-500/20 text-green-400"
                      : llmAnalysis.qualitative_fit === "good_match"
                      ? "bg-blue-500/20 text-blue-400"
                      : llmAnalysis.qualitative_fit === "partial_match"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {llmAnalysis.qualitative_fit.replace("_", " ").toUpperCase()}
                </span>
                <span className="text-xs text-muted-foreground">
                  Interview Readiness: {llmAnalysis.interview_readiness}/10
                </span>
              </div>
              <p className="text-sm text-foreground">
                {llmAnalysis.fit_explanation}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="text-xs font-medium text-green-400 uppercase">
                Strengths
              </h4>
              {llmAnalysis.strengths.map((s, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 rounded-lg bg-green-500/5 border border-green-500/20 px-3 py-2"
                >
                  <span className="text-green-400 mt-0.5">+</span>
                  <span className="text-sm text-foreground">{s}</span>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              <h4 className="text-xs font-medium text-red-400 uppercase">
                Gaps
              </h4>
              {llmAnalysis.gaps.map((g, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 rounded-lg bg-red-500/5 border border-red-500/20 px-3 py-2"
                >
                  <span className="text-red-400 mt-0.5">-</span>
                  <span className="text-sm text-foreground">{g}</span>
                </div>
              ))}
            </div>
          </div>

          {llmAnalysis.bullet_rewrites.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-medium text-muted-foreground uppercase">
                Bullet Rewrites
              </h4>
              {llmAnalysis.bullet_rewrites.map((b, i) => (
                <div key={i} className="rounded-lg border border-border p-4 space-y-2">
                  <div className="space-y-1">
                    <span className="text-xs text-red-400">Original:</span>
                    <p className="text-sm text-muted-foreground">{b.original}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-green-400">Improved:</span>
                    <p className="text-sm text-foreground">{b.improved}</p>
                  </div>
                  <p className="text-xs text-muted-foreground italic">
                    {b.reason}
                  </p>
                  <button
                    onClick={() => navigator.clipboard.writeText(b.improved)}
                    className="text-xs text-primary hover:text-primary/80"
                  >
                    Copy
                  </button>
                </div>
              ))}
            </div>
          )}

          {llmAnalysis.skills_section_rewrite && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-medium text-muted-foreground uppercase">
                  Optimized Skills Section
                </h4>
                <button
                  onClick={() =>
                    navigator.clipboard.writeText(
                      llmAnalysis.skills_section_rewrite
                    )
                  }
                  className="text-xs text-primary hover:text-primary/80"
                >
                  Copy
                </button>
              </div>
              <div className="rounded-lg bg-secondary/30 p-3">
                <p className="text-sm text-foreground whitespace-pre-wrap">
                  {llmAnalysis.skills_section_rewrite}
                </p>
              </div>
            </div>
          )}

          {llmAnalysis.interview_topics.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-medium text-muted-foreground uppercase">
                Likely Interview Topics
              </h4>
              <div className="flex flex-wrap gap-2">
                {llmAnalysis.interview_topics.map((t, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-full bg-primary/10 text-xs text-primary"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {llmAnalysis.overall_recommendation && (
            <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
              <h4 className="text-xs font-medium text-primary uppercase mb-2">
                Recommendation
              </h4>
              <p className="text-sm text-foreground">
                {llmAnalysis.overall_recommendation}
              </p>
            </div>
          )}
        </>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            Prioritized Suggestions
          </h3>
          {suggestions.map((s, i) => (
            <div
              key={i}
              className="rounded-lg border border-border p-4 flex items-start gap-3"
            >
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium border whitespace-nowrap ${priorityColor(
                  s.priority
                )}`}
              >
                {s.priority}
              </span>
              <div className="flex-1 min-w-0">
                <h5 className="text-sm font-medium text-foreground">
                  {s.title}
                </h5>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {s.description}
                </p>
              </div>
              {s.estimated_impact > 0 && (
                <span className="text-xs text-green-400 whitespace-nowrap">
                  +{s.estimated_impact} pts
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
