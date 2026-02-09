"use client";

import { useEffect, useState } from "react";
import { getScoreRingColor, getScoreColor } from "@/lib/utils";

interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: "sm" | "lg";
}

export default function ScoreGauge({
  score,
  label,
  size = "sm",
}: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const dimensions = size === "lg" ? 180 : 120;
  const strokeWidth = size === "lg" ? 10 : 8;
  const radius = (dimensions - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: dimensions, height: dimensions }}>
        <svg
          width={dimensions}
          height={dimensions}
          className="transform -rotate-90"
        >
          <circle
            cx={dimensions / 2}
            cy={dimensions / 2}
            r={radius}
            fill="none"
            stroke="hsl(217 33% 17%)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={dimensions / 2}
            cy={dimensions / 2}
            r={radius}
            fill="none"
            className={getScoreRingColor(score)}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: "stroke-dashoffset 1.5s ease-out",
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className={`font-bold ${getScoreColor(score)} ${
              size === "lg" ? "text-4xl" : "text-2xl"
            }`}
          >
            {animatedScore}
          </span>
          {size === "lg" && (
            <span className="text-xs text-muted-foreground mt-1">/ 100</span>
          )}
        </div>
      </div>
      <span
        className={`font-medium text-muted-foreground ${
          size === "lg" ? "text-sm" : "text-xs"
        }`}
      >
        {label}
      </span>
    </div>
  );
}
