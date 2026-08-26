"use client";

import { useState } from "react";
import type { Posting } from "@/lib/api";

function scoreColor(score: number) {
  if (score >= 0.5) return "text-board-teal border-board-teal";
  if (score >= 0.25) return "text-board-amber border-board-amber";
  return "text-board-red border-board-red";
}

export default function JobRow({
  job,
  index,
}: {
  job: Posting;
  index: number;
}) {
  const [open, setOpen] = useState(false);
  const skills = job.matched_skills
    ? job.matched_skills.split(",").map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div
      className="animate-flip-in border-b border-board-line last:border-b-0"
      style={{ animationDelay: `${Math.min(index * 40, 600)}ms` }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left px-5 py-4 flex flex-wrap md:flex-nowrap items-center gap-4 hover:bg-board-panel/60 transition-colors"
      >
        <div
          className={`font-mono-board text-sm px-2 py-1 border tabular-nums shrink-0 ${scoreColor(
            job.match_score
          )}`}
        >
          {Math.round(job.match_score * 100)}%
        </div>

        <div className="flex-1 min-w-[200px]">
          <div className="font-sans-board text-board-text font-medium leading-snug">
            {job.title}
          </div>
          <div className="font-mono-board text-xs text-board-slate mt-0.5">
            {job.company || "Unknown"} · {job.location || "—"}
          </div>
        </div>

        <div className="font-mono-board text-[11px] tracking-[0.1em] text-board-slate shrink-0">
          {job.source?.toUpperCase()}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-5 pt-1 border-t border-board-line/50 bg-board-panel/40">
          {skills.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3 mt-3">
              {skills.map((skill) => (
                <span
                  key={skill}
                  className="font-mono-board text-[11px] px-2 py-1 border border-board-teal/40 text-board-teal"
                >
                  {skill}
                </span>
              ))}
            </div>
          )}
          {job.description && (
            <p className="font-sans-board text-sm text-board-text/80 leading-relaxed line-clamp-6">
              {job.description}
            </p>
          )}
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 font-mono-board text-xs text-board-amber border border-board-amber px-3 py-1.5 hover:bg-board-amber hover:text-board-bg transition-colors"
            >
              APPLY →
            </a>
          )}
        </div>
      )}
    </div>
  );
}
