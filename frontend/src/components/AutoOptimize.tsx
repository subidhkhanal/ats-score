"use client";

import { useState } from "react";
import { OptimizeResponse } from "@/lib/types";

interface AutoOptimizeProps {
  optimization: OptimizeResponse | null;
  onOptimize: () => void;
  optimizing: boolean;
}

export default function AutoOptimize({
  optimization,
  onOptimize,
  optimizing,
}: AutoOptimizeProps) {
  const [acceptedChanges, setAcceptedChanges] = useState<Set<number>>(
    new Set()
  );

  if (!optimization) {
    return (
      <div className="space-y-4">
        <div className="rounded-xl border border-border bg-card p-8 text-center space-y-4">
          <h3 className="text-lg font-semibold text-foreground">
            Auto-Optimize Your Resume
          </h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            AI will rewrite your resume to maximize ATS keyword matching while
            keeping everything 100% truthful. Only your existing skills and
            experience are used.
          </p>
          <button
            onClick={onOptimize}
            disabled={optimizing}
            className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {optimizing ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Optimizing...
              </span>
            ) : (
              "Optimize My Resume"
            )}
          </button>
          <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 px-4 py-2">
            <p className="text-xs text-yellow-400">
              Only your existing skills and experience are used — nothing
              fabricated
            </p>
          </div>
        </div>
      </div>
    );
  }

  const toggleChange = (idx: number) => {
    const newSet = new Set(acceptedChanges);
    if (newSet.has(idx)) {
      newSet.delete(idx);
    } else {
      newSet.add(idx);
    }
    setAcceptedChanges(newSet);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {optimization.input_format === "latex" && (
        <div className="rounded-lg bg-purple-500/10 border border-purple-500/20 px-4 py-2">
          <p className="text-xs text-purple-400">
            LaTeX Mode — output is a compilable .tex file
          </p>
        </div>
      )}

      {/* Score comparison */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
          Score Comparison
        </h3>
        <div className="flex items-center justify-center gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-muted-foreground">
              {optimization.original_score}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Original</div>
          </div>
          <div className="text-2xl text-muted-foreground">→</div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400">
              {optimization.optimized_score}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Optimized</div>
          </div>
          <div
            className={`text-center px-3 py-1 rounded-lg ${
              optimization.score_delta > 0
                ? "bg-green-500/20 text-green-400"
                : "bg-yellow-500/20 text-yellow-400"
            }`}
          >
            <div className="text-lg font-bold">
              {optimization.score_delta > 0 ? "+" : ""}
              {optimization.score_delta}
            </div>
            <div className="text-xs">pts</div>
          </div>
        </div>
      </div>

      {/* Keywords added */}
      {optimization.keywords_added.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-green-400 uppercase">
            Keywords Added
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {optimization.keywords_added.map((kw, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-full bg-green-500/20 text-xs text-green-400 border border-green-500/30"
              >
                + {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Keywords impossible */}
      {optimization.keywords_impossible.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-orange-400 uppercase">
            Could Not Add
          </h4>
          {optimization.keywords_impossible.map((kw, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-lg bg-orange-500/5 border border-orange-500/20 px-3 py-2"
            >
              <span className="text-orange-400 text-sm">!</span>
              <div>
                <span className="text-sm text-foreground font-medium">
                  {kw.keyword}
                </span>
                <p className="text-xs text-muted-foreground">{kw.reason}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Before/After diff */}
      <div className="space-y-3">
        <h4 className="text-xs font-medium text-muted-foreground uppercase">
          Changes
        </h4>
        {optimization.changes.map((change, i) => (
          <div
            key={i}
            className="rounded-lg border border-border p-4 space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={acceptedChanges.has(i)}
                  onChange={() => toggleChange(i)}
                  className="rounded"
                />
                <span className="text-xs font-medium text-primary uppercase">
                  {change.section}
                </span>
                <span className="text-xs text-muted-foreground">
                  {change.change_type}
                </span>
              </div>
              {change.keywords_added.length > 0 && (
                <div className="flex gap-1">
                  {change.keywords_added.map((kw, j) => (
                    <span
                      key={j}
                      className="px-1.5 py-0.5 rounded bg-green-500/20 text-xs text-green-400"
                    >
                      +{kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
            {change.original && (
              <div className="rounded bg-red-500/5 border border-red-500/10 p-2">
                <span className="text-xs text-red-400 block mb-1">
                  Original:
                </span>
                <p className="text-xs text-foreground/70 whitespace-pre-wrap">
                  {change.original}
                </p>
              </div>
            )}
            <div className="rounded bg-green-500/5 border border-green-500/10 p-2">
              <span className="text-xs text-green-400 block mb-1">
                Optimized:
              </span>
              <p className="text-xs text-foreground whitespace-pre-wrap">
                {change.optimized}
              </p>
            </div>
            <p className="text-xs text-muted-foreground italic">
              {change.reason}
            </p>
          </div>
        ))}

        {optimization.optimized_bullets.map((bc, i) => (
          <div
            key={`bullet-${i}`}
            className="rounded-lg border border-border p-4 space-y-2"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-primary uppercase">
                {bc.section}
              </span>
              {bc.keywords_added.map((kw, j) => (
                <span
                  key={j}
                  className="px-1.5 py-0.5 rounded bg-green-500/20 text-xs text-green-400"
                >
                  +{kw}
                </span>
              ))}
            </div>
            <div className="rounded bg-red-500/5 border border-red-500/10 p-2">
              <p className="text-xs text-foreground/70">{bc.original}</p>
            </div>
            <div className="rounded bg-green-500/5 border border-green-500/10 p-2">
              <p className="text-xs text-foreground">{bc.optimized}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Validation */}
      {!optimization.validation.valid && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
          <p className="text-xs text-red-400">{optimization.validation.message}</p>
          {optimization.fabricated_skills_removed.length > 0 && (
            <p className="text-xs text-red-400 mt-1">
              Fabricated skills detected and removed:{" "}
              {optimization.fabricated_skills_removed.join(", ")}
            </p>
          )}
        </div>
      )}

      {optimization.latex_validation &&
        !optimization.latex_validation.valid && (
          <div className="rounded-lg bg-orange-500/10 border border-orange-500/20 p-3">
            <p className="text-xs text-orange-400 font-medium mb-1">
              LaTeX Validation Issues:
            </p>
            {optimization.latex_validation.errors.map((e, i) => (
              <p key={i} className="text-xs text-orange-400">
                {e}
              </p>
            ))}
          </div>
        )}

      {/* Download buttons */}
      <div className="flex items-center gap-3 flex-wrap">
        {optimization.optimized_latex && (
          <>
            <button
              onClick={() =>
                handleDownload(
                  optimization.optimized_latex!,
                  "optimized_resume.tex"
                )
              }
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
            >
              Download .tex
            </button>
            <button
              onClick={() => handleCopy(optimization.optimized_latex!)}
              className="px-4 py-2 rounded-lg bg-secondary text-foreground text-sm font-medium hover:bg-secondary/80"
            >
              Copy LaTeX
            </button>
          </>
        )}
        <button
          onClick={() =>
            handleDownload(optimization.optimized_text, "optimized_resume.txt")
          }
          className="px-4 py-2 rounded-lg bg-secondary text-foreground text-sm font-medium hover:bg-secondary/80"
        >
          Download .txt
        </button>
        <button
          onClick={() => handleCopy(optimization.optimized_text)}
          className="px-4 py-2 rounded-lg bg-secondary text-foreground text-sm font-medium hover:bg-secondary/80"
        >
          Copy Text
        </button>
      </div>
    </div>
  );
}
