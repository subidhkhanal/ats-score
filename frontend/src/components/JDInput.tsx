"use client";

interface JDInputProps {
  jdText: string;
  onJDTextChange: (text: string) => void;
}

export default function JDInput({ jdText, onJDTextChange }: JDInputProps) {
  const wordCount = jdText.trim() ? jdText.trim().split(/\s+/).length : 0;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-foreground">
        Job Description
      </h2>

      <div className="relative">
        <textarea
          value={jdText}
          onChange={(e) => onJDTextChange(e.target.value)}
          placeholder="Paste the full job description here..."
          className="w-full h-64 rounded-lg bg-secondary/50 border border-border p-4 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 scrollbar-thin"
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-muted-foreground">
            {wordCount} words
          </span>
          {jdText && (
            <button
              onClick={() => onJDTextChange("")}
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
