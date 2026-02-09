"use client";

import { useState } from "react";
import { KeywordMatchResult } from "@/lib/types";

interface KeywordAnalysisProps {
  results: KeywordMatchResult[];
}

export default function KeywordAnalysis({ results }: KeywordAnalysisProps) {
  const [filter, setFilter] = useState<"all" | "required" | "preferred">("all");
  const [showFound, setShowFound] = useState(true);
  const [showMissing, setShowMissing] = useState(true);

  const filtered = results.filter((r) => {
    if (filter !== "all" && r.category !== filter) return false;
    if (!showFound && r.found) return false;
    if (!showMissing && !r.found) return false;
    return true;
  });

  const found = results.filter((r) => r.found);
  const missing = results.filter((r) => !r.found);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Keyword Analysis
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-green-400">
            {found.length} found
          </span>
          <span className="text-xs text-muted-foreground">/</span>
          <span className="text-xs text-red-400">
            {missing.length} missing
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {(["all", "required", "preferred"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === f
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            {f === "all" ? "All" : f === "required" ? "Required" : "Preferred"}
          </button>
        ))}
        <div className="flex items-center gap-2 ml-auto">
          <label className="flex items-center gap-1 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={showFound}
              onChange={(e) => setShowFound(e.target.checked)}
              className="rounded"
            />
            Found
          </label>
          <label className="flex items-center gap-1 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={showMissing}
              onChange={(e) => setShowMissing(e.target.checked)}
              className="rounded"
            />
            Missing
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-green-400 uppercase">
            Found ({filtered.filter((r) => r.found).length})
          </h4>
          {filtered
            .filter((r) => r.found)
            .map((r, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-lg bg-green-500/5 border border-green-500/20 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-green-400 text-sm">&#10003;</span>
                  <span className="text-sm text-foreground">{r.keyword}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    {r.match_type}
                  </span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      r.category === "required"
                        ? "bg-red-500/20 text-red-400"
                        : "bg-blue-500/20 text-blue-400"
                    }`}
                  >
                    {r.category}
                  </span>
                  {r.location_in_resume && (
                    <span className="text-xs text-muted-foreground">
                      in {r.location_in_resume}
                    </span>
                  )}
                </div>
              </div>
            ))}
        </div>

        <div className="space-y-2">
          <h4 className="text-xs font-medium text-red-400 uppercase">
            Missing ({filtered.filter((r) => !r.found).length})
          </h4>
          {filtered
            .filter((r) => !r.found)
            .map((r, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-lg bg-red-500/5 border border-red-500/20 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-red-400 text-sm">&#10007;</span>
                  <span className="text-sm text-foreground">{r.keyword}</span>
                </div>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${
                    r.category === "required"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {r.category}
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
