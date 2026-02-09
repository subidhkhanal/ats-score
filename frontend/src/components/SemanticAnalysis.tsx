"use client";

import { SemanticResult } from "@/lib/types";
import { getScoreBgColor } from "@/lib/utils";

interface SemanticAnalysisProps {
  results: SemanticResult;
}

export default function SemanticAnalysis({ results }: SemanticAnalysisProps) {
  const sections = [
    {
      name: "Skills Match",
      value: results.section_similarities.skills || results.skills_similarity * 100,
      desc: "How well your skills align with the job requirements",
    },
    {
      name: "Experience Match",
      value: results.section_similarities.experience || results.experience_similarity * 100,
      desc: "How closely your experience matches the responsibilities",
    },
    {
      name: "Education Match",
      value: results.section_similarities.education || results.education_similarity * 100,
      desc: "How well your education fits the qualifications",
    },
    {
      name: "Overall Similarity",
      value: results.section_similarities.overall || results.overall_similarity * 100,
      desc: "Full document semantic similarity",
    },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
        Semantic Analysis
      </h3>
      <p className="text-xs text-muted-foreground">
        AI-powered meaning-based comparison between your resume sections and job
        requirements
      </p>

      <div className="space-y-4">
        {sections.map((section) => {
          const val = Math.round(section.value);
          return (
            <div key={section.name} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">{section.name}</span>
                <span className="text-sm font-semibold text-foreground">
                  {val}%
                </span>
              </div>
              <div className="h-2.5 rounded-full bg-secondary overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${getScoreBgColor(val)}`}
                  style={{ width: `${val}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">{section.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
