"use client";

import { useState } from "react";
import { useAnalysis } from "@/hooks/useAnalysis";
import ResumeUpload from "@/components/ResumeUpload";
import JDInput from "@/components/JDInput";
import ScoreGauge from "@/components/ScoreGauge";
import RadarChart from "@/components/RadarChart";
import RecruiterView from "@/components/RecruiterView";
import KeywordAnalysis from "@/components/KeywordAnalysis";
import SemanticAnalysis from "@/components/SemanticAnalysis";
import StructureCheck from "@/components/StructureCheck";
import AIRecommendations from "@/components/AIRecommendations";
import AutoOptimize from "@/components/AutoOptimize";

type TabId =
  | "overview"
  | "recruiter"
  | "keywords"
  | "semantic"
  | "structure"
  | "ai"
  | "optimize";

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | undefined>();
  const [activeTab, setActiveTab] = useState<TabId>("overview");

  const {
    analysis,
    optimization,
    loading,
    optimizing,
    error,
    analyze,
    optimize,
  } = useAnalysis();

  const handleAnalyze = async () => {
    if (!resumeText && !resumeFile) {
      alert("Please provide a resume");
      return;
    }
    if (!jdText.trim()) {
      alert("Please provide a job description");
      return;
    }
    await analyze(resumeText, jdText, resumeFile);
  };

  const handleOptimize = async () => {
    await optimize(resumeText, jdText, resumeFile);
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: "overview", label: "Score Overview" },
    { id: "recruiter", label: "Recruiter View" },
    { id: "keywords", label: "Keywords" },
    { id: "semantic", label: "Semantic" },
    { id: "structure", label: "Structure" },
    { id: "ai", label: "AI Insights" },
    { id: "optimize", label: "Auto-Optimize" },
  ];

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <svg className="w-5 h-5 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  ResumeRadar
                </h1>
                <p className="text-xs text-muted-foreground">
                  AI-Powered ATS Score Analyzer
                </p>
              </div>
            </div>
            {analysis && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  Score:
                </span>
                <span className="text-lg font-bold text-foreground">
                  {analysis.overall_score}%
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        {!analysis && (
          <div className="space-y-8">
            <div className="text-center space-y-3 max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold text-foreground">
                See How Your Resume Scores
              </h2>
              <p className="text-muted-foreground">
                Upload your resume and paste a job description to get an
                AI-powered ATS analysis — the way a FAANG recruiter would see
                it.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="rounded-xl border border-border bg-card p-6">
                <ResumeUpload
                  resumeText={resumeText}
                  onResumeTextChange={setResumeText}
                  onFileChange={setResumeFile}
                  file={resumeFile}
                />
              </div>
              <div className="rounded-xl border border-border bg-card p-6">
                <JDInput jdText={jdText} onJDTextChange={setJdText} />
              </div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={loading || (!resumeText && !resumeFile) || !jdText.trim()}
                className="px-8 py-3 rounded-lg bg-primary text-primary-foreground font-semibold text-base hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
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
                    Analyzing...
                  </span>
                ) : (
                  "Analyze Resume"
                )}
              </button>
            </div>

            {error && (
              <div className="max-w-md mx-auto rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-center">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
          </div>
        )}

        {/* Results Section */}
        {analysis && (
          <div className="space-y-6">
            {/* New Analysis Button */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => window.location.reload()}
                className="text-sm text-primary hover:text-primary/80 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                New Analysis
              </button>
            </div>

            {/* Tabs */}
            <div className="border-b border-border">
              <div className="flex gap-1 overflow-x-auto scrollbar-thin pb-px">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                      activeTab === tab.id
                        ? "border-primary text-primary"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px]">
              {activeTab === "overview" && (
                <div className="space-y-8">
                  <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
                    <ScoreGauge
                      score={analysis.overall_score}
                      label="Overall ATS Score"
                      size="lg"
                    />
                    <div className="flex gap-8">
                      <ScoreGauge
                        score={analysis.keyword_score}
                        label="Keywords"
                      />
                      <ScoreGauge
                        score={analysis.semantic_score}
                        label="Semantic"
                      />
                      <ScoreGauge
                        score={analysis.structure_score}
                        label="Structure"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="rounded-xl border border-border bg-card p-6">
                      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                        Score Breakdown
                      </h3>
                      <RadarChart
                        data={{
                          skills:
                            analysis.semantic_results.section_similarities
                              .skills || 0,
                          experience:
                            analysis.semantic_results.section_similarities
                              .experience || 0,
                          education:
                            analysis.semantic_results.section_similarities
                              .education || 0,
                          projects:
                            analysis.structure_results.details.has_projects
                              ? 75
                              : 25,
                          format: analysis.structure_score,
                        }}
                      />
                    </div>

                    <div className="rounded-xl border border-border bg-card p-6 space-y-4">
                      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                        Quick Summary
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Keywords Found
                          </span>
                          <span className="text-sm font-medium text-foreground">
                            {
                              analysis.keyword_results.filter((k) => k.found)
                                .length
                            }
                            /{analysis.keyword_results.length}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Recruiter Status
                          </span>
                          <span
                            className={`text-sm font-medium px-2 py-0.5 rounded ${
                              analysis.recruiter_status === "SHORTLIST"
                                ? "bg-green-500/20 text-green-400"
                                : analysis.recruiter_status === "REVIEW"
                                ? "bg-yellow-500/20 text-yellow-400"
                                : analysis.recruiter_status === "MAYBE"
                                ? "bg-orange-500/20 text-orange-400"
                                : "bg-red-500/20 text-red-400"
                            }`}
                          >
                            {analysis.recruiter_status}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Estimated Rank
                          </span>
                          <span className="text-sm font-medium text-foreground">
                            {analysis.rank_estimate}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Job Title
                          </span>
                          <span className="text-sm font-medium text-foreground truncate ml-4">
                            {analysis.parsed_jd.title || "—"}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Experience Level
                          </span>
                          <span className="text-sm font-medium text-foreground capitalize">
                            {analysis.parsed_jd.experience_level}
                          </span>
                        </div>
                      </div>

                      {analysis.suggestions.length > 0 && (
                        <div className="pt-2 border-t border-border">
                          <h4 className="text-xs font-medium text-muted-foreground uppercase mb-2">
                            Top Suggestion
                          </h4>
                          <p className="text-sm text-foreground">
                            {analysis.suggestions[0].title}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {analysis.suggestions[0].description}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "recruiter" && (
                <RecruiterView analysis={analysis} />
              )}

              {activeTab === "keywords" && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <KeywordAnalysis results={analysis.keyword_results} />
                </div>
              )}

              {activeTab === "semantic" && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <SemanticAnalysis results={analysis.semantic_results} />
                </div>
              )}

              {activeTab === "structure" && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <StructureCheck results={analysis.structure_results} />
                </div>
              )}

              {activeTab === "ai" && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <AIRecommendations
                    llmAnalysis={analysis.llm_analysis}
                    suggestions={analysis.suggestions}
                  />
                </div>
              )}

              {activeTab === "optimize" && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <AutoOptimize
                    optimization={optimization}
                    onOptimize={handleOptimize}
                    optimizing={optimizing}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-16 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-xs text-muted-foreground">
            ResumeRadar — AI-Powered ATS Score Analyzer
          </p>
        </div>
      </footer>
    </main>
  );
}
