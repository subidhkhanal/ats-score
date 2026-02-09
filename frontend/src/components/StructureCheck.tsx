"use client";

import { StructureResult } from "@/lib/types";

interface StructureCheckProps {
  results: StructureResult;
}

export default function StructureCheck({ results }: StructureCheckProps) {
  const { details } = results;

  const checks = [
    { label: "Name detected", passed: details.has_name, category: "Contact" },
    { label: "Email found", passed: details.has_email, category: "Contact" },
    { label: "Phone found", passed: details.has_phone, category: "Contact" },
    { label: "LinkedIn URL", passed: details.has_linkedin, category: "Contact" },
    { label: "GitHub/Portfolio", passed: details.has_github, category: "Contact" },
    { label: "Summary/About section", passed: details.has_summary, category: "Sections" },
    { label: "Experience section", passed: details.has_experience, category: "Sections" },
    { label: "Education section", passed: details.has_education, category: "Sections" },
    { label: "Skills section", passed: details.has_skills, category: "Sections" },
    { label: "Projects section", passed: details.has_projects, category: "Sections" },
    { label: "Standard headers", passed: details.has_standard_headers, category: "Formatting" },
    { label: "Consistent dates", passed: details.has_consistent_dates, category: "Formatting" },
  ];

  const categories = ["Contact", "Sections", "Formatting"];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Structure Check
        </h3>
        <span className="text-sm font-semibold text-foreground">
          {results.total_score}/100
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-lg bg-secondary/50 p-3 text-center">
          <div className="text-lg font-semibold text-foreground">
            {results.contact_score}/25
          </div>
          <div className="text-xs text-muted-foreground">Contact</div>
        </div>
        <div className="rounded-lg bg-secondary/50 p-3 text-center">
          <div className="text-lg font-semibold text-foreground">
            {results.sections_score}/25
          </div>
          <div className="text-xs text-muted-foreground">Sections</div>
        </div>
        <div className="rounded-lg bg-secondary/50 p-3 text-center">
          <div className="text-lg font-semibold text-foreground">
            {results.length_score}/25
          </div>
          <div className="text-xs text-muted-foreground">Length</div>
        </div>
        <div className="rounded-lg bg-secondary/50 p-3 text-center">
          <div className="text-lg font-semibold text-foreground">
            {results.formatting_score}/25
          </div>
          <div className="text-xs text-muted-foreground">Format</div>
        </div>
      </div>

      {categories.map((category) => (
        <div key={category} className="space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground uppercase">
            {category}
          </h4>
          <div className="space-y-1">
            {checks
              .filter((c) => c.category === category)
              .map((check, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 bg-secondary/30"
                >
                  <span
                    className={
                      check.passed ? "text-green-400" : "text-red-400"
                    }
                  >
                    {check.passed ? "\u2713" : "\u2717"}
                  </span>
                  <span className="text-sm text-foreground">{check.label}</span>
                </div>
              ))}
          </div>
        </div>
      ))}

      {details.formatting_issues.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-orange-400 uppercase">
            Issues Found
          </h4>
          {details.formatting_issues.map((issue, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-lg px-3 py-2 bg-orange-500/5 border border-orange-500/20"
            >
              <span className="text-orange-400 mt-0.5">!</span>
              <span className="text-sm text-foreground">{issue}</span>
            </div>
          ))}
        </div>
      )}

      <div className="rounded-lg bg-secondary/30 px-3 py-2">
        <span className="text-xs text-muted-foreground">
          {details.word_count} words / ~{details.estimated_pages} page(s)
        </span>
      </div>
    </div>
  );
}
