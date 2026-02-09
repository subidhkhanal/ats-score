import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

export function getScoreBgColor(score: number): string {
  if (score >= 80) return "bg-green-400";
  if (score >= 60) return "bg-yellow-400";
  if (score >= 40) return "bg-orange-400";
  return "bg-red-400";
}

export function getScoreRingColor(score: number): string {
  if (score >= 80) return "stroke-green-400";
  if (score >= 60) return "stroke-yellow-400";
  if (score >= 40) return "stroke-orange-400";
  return "stroke-red-400";
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "SHORTLIST":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "REVIEW":
      return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    case "MAYBE":
      return "bg-orange-500/20 text-orange-400 border-orange-500/30";
    case "AUTO_REJECTED":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border-gray-500/30";
  }
}

export function getStatusLabel(status: string): string {
  switch (status) {
    case "SHORTLIST":
      return "SHORTLIST";
    case "REVIEW":
      return "REVIEW";
    case "MAYBE":
      return "MAYBE";
    case "AUTO_REJECTED":
      return "REJECTED";
    default:
      return status;
  }
}
