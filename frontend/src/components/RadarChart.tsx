"use client";

import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

interface RadarChartProps {
  data: {
    skills: number;
    experience: number;
    education: number;
    projects: number;
    format: number;
  };
}

export default function RadarChart({ data }: RadarChartProps) {
  const chartData = [
    { subject: "Skills", value: data.skills },
    { subject: "Experience", value: data.experience },
    { subject: "Education", value: data.education },
    { subject: "Projects", value: data.projects },
    { subject: "Format", value: data.format },
  ];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={chartData} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="hsl(217 33% 20%)" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "hsl(215 20% 65%)", fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "hsl(215 20% 65%)", fontSize: 10 }}
          />
          <Radar
            dataKey="value"
            stroke="hsl(217 91% 60%)"
            fill="hsl(217 91% 60%)"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  );
}
