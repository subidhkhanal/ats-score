"use client";

import { ATSAnalysisResponse } from "@/lib/types";
import { getStatusColor, getStatusLabel } from "@/lib/utils";

interface RecruiterViewProps {
  analysis: ATSAnalysisResponse;
}

export default function RecruiterView({ analysis }: RecruiterViewProps) {
  const { parsed_resume, overall_score, recruiter_status, rank_estimate, keyword_results } = analysis;
  const matchedCount = keyword_results.filter((k) => k.found).length;
  const totalCount = keyword_results.length;

  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Recruiter Simulation View
        </h3>
        <span className="text-xs text-muted-foreground">
          How a recruiter sees your application in their ATS
        </span>
      </div>

      <div className="rounded-lg border border-border bg-secondary/30 p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h2 className="text-xl font-semibold text-foreground">
              {parsed_resume.contact.name || "Candidate"}
            </h2>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              {parsed_resume.contact.email && (
                <span>{parsed_resume.contact.email}</span>
              )}
              {parsed_resume.contact.phone && (
                <span>{parsed_resume.contact.phone}</span>
              )}
              {parsed_resume.contact.location && (
                <span>{parsed_resume.contact.location}</span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-3xl font-bold text-foreground">
                {overall_score}%
              </div>
              <div className="text-xs text-muted-foreground">Match Score</div>
            </div>
            <span
              className={`inline-flex items-center rounded-md border px-3 py-1.5 text-sm font-semibold ${getStatusColor(
                recruiter_status
              )}`}
            >
              {getStatusLabel(recruiter_status)}
            </span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-4 gap-4">
          <div className="rounded-lg bg-background/50 p-3 text-center">
            <div className="text-lg font-semibold text-foreground">
              {matchedCount}/{totalCount}
            </div>
            <div className="text-xs text-muted-foreground">Keywords Matched</div>
          </div>
          <div className="rounded-lg bg-background/50 p-3 text-center">
            <div className="text-lg font-semibold text-foreground">
              {analysis.parsed_jd.experience_level}
            </div>
            <div className="text-xs text-muted-foreground">Experience Level</div>
          </div>
          <div className="rounded-lg bg-background/50 p-3 text-center">
            <div className="text-lg font-semibold text-foreground">
              {rank_estimate}
            </div>
            <div className="text-xs text-muted-foreground">Estimated Rank</div>
          </div>
          <div className="rounded-lg bg-background/50 p-3 text-center">
            <div className="text-lg font-semibold text-foreground">
              {parsed_resume.estimated_pages}
            </div>
            <div className="text-xs text-muted-foreground">Page(s)</div>
          </div>
        </div>

        {parsed_resume.skills.length > 0 && (
          <div className="mt-4">
            <div className="text-xs font-medium text-muted-foreground mb-2">
              Detected Skills
            </div>
            <div className="flex flex-wrap gap-1.5">
              {parsed_resume.skills.slice(0, 15).map((skill, i) => (
                <span
                  key={i}
                  className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs text-primary"
                >
                  {skill}
                </span>
              ))}
              {parsed_resume.skills.length > 15 && (
                <span className="text-xs text-muted-foreground">
                  +{parsed_resume.skills.length - 15} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
