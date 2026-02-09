"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface ResumeUploadProps {
  resumeText: string;
  onResumeTextChange: (text: string) => void;
  onFileChange: (file: File | undefined) => void;
  file: File | undefined;
}

export default function ResumeUpload({
  resumeText,
  onResumeTextChange,
  onFileChange,
  file,
}: ResumeUploadProps) {
  const [isLatex, setIsLatex] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const f = acceptedFiles[0];
        if (f.size > 5 * 1024 * 1024) {
          alert("File size must be under 5MB");
          return;
        }
        onFileChange(f);

        if (f.name.endsWith(".txt") || f.name.endsWith(".tex")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            const text = e.target?.result as string;
            onResumeTextChange(text);
            setIsLatex(
              text.includes("\\documentclass") ||
                text.includes("\\begin{document}")
            );
          };
          reader.readAsText(f);
        }
      }
    },
    [onFileChange, onResumeTextChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
      "application/x-tex": [".tex"],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
  });

  const handleTextChange = (text: string) => {
    onResumeTextChange(text);
    onFileChange(undefined);
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

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-primary bg-primary/5"
            : file
            ? "border-green-500/50 bg-green-500/5"
            : "border-border hover:border-primary/50"
        }`}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="space-y-1">
            <p className="text-sm text-green-400 font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(file.size / 1024).toFixed(1)} KB
            </p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFileChange(undefined);
                onResumeTextChange("");
              }}
              className="text-xs text-red-400 hover:text-red-300 mt-1"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex justify-center">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">
              Drop your resume here, or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, DOCX, TXT, TEX (max 5MB)
            </p>
          </div>
        )}
      </div>

      <div className="relative">
        <p className="text-sm text-muted-foreground mb-2">
          Or paste your resume text:
        </p>
        <textarea
          value={resumeText}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Paste your resume here..."
          className="w-full h-48 rounded-lg bg-secondary/50 border border-border p-4 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 scrollbar-thin"
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
