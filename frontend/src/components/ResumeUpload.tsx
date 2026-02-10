"use client";

import { useState } from "react";

interface ResumeUploadProps {
  resumeText: string;
  onResumeTextChange: (text: string) => void;
}

export default function ResumeUpload({
  resumeText,
  onResumeTextChange,
}: ResumeUploadProps) {
  const [isLatex, setIsLatex] = useState(false);

  const handleTextChange = (text: string) => {
    onResumeTextChange(text);
    setIsLatex(
      text.includes("\\documentclass") || text.includes("\\begin{document}")
    );
  };

  const wordCount = resumeText.trim()
    ? resumeText.trim().split(/\s+/).length
    : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">Resume</h2>
        {isLatex && (
          <span className="inline-flex items-center gap-1 rounded-full bg-purple-500/20 px-3 py-1 text-xs font-medium text-purple-400 border border-purple-500/30">
            LaTeX Detected
          </span>
        )}
      </div>

      <div className="relative">
        <p className="text-sm text-muted-foreground mb-2">
          Paste your LaTeX resume code:
        </p>
        <textarea
          value={resumeText}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder={"\\documentclass{resume}\n\\begin{document}\n  % Paste your LaTeX resume here...\n\\end{document}"}
          className="w-full h-64 rounded-lg bg-secondary/50 border border-border p-4 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 scrollbar-thin font-mono"
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-muted-foreground">
            {wordCount} words
          </span>
          {resumeText && (
            <button
              onClick={() => handleTextChange("")}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Clear
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
