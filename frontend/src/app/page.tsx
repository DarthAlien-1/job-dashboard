"use client";

import { useState } from "react";
import { uploadCV, type Posting } from "@/lib/api";
import JobRow from "@/components/JobRow";

export default function Home() {
  const [allMatchedJobs, setAllMatchedJobs] = useState<Posting[]>([]);
  const [extractedSkills, setExtractedSkills] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters for after a CV is uploaded
  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(0);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await uploadCV(file);
      setExtractedSkills(result.extracted_skills);
      setAllMatchedJobs(result.jobs);
    } catch (err) {
      setError("Failed to process CV. Please check if the backend API is running.");
    } finally {
      setUploading(false);
    }
  };

  const clearCV = () => {
    setExtractedSkills([]);
    setAllMatchedJobs([]);
    setSearch("");
    setMinScore(0);
    setError(null);
  };

  // Filter the CV-matched jobs locally by user search / score threshold
  const filteredJobs = allMatchedJobs.filter((job) => {
    const matchesSearch =
      !search ||
      job.title.toLowerCase().includes(search.toLowerCase()) ||
      (job.company && job.company.toLowerCase().includes(search.toLowerCase()));

    const matchesScore = job.match_score >= minScore;

    return matchesSearch && matchesScore;
  });

  const avgMatchScore =
    allMatchedJobs.length > 0
      ? Math.round(
          (allMatchedJobs.reduce((acc, job) => acc + job.match_score, 0) /
            allMatchedJobs.length) *
            100
        )
      : 0;

  return (
    <main className="min-h-screen max-w-4xl mx-auto px-4 py-10 md:py-16">
      <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="font-mono-board text-xs tracking-[0.2em] text-board-slate mb-2">
            AI RESUME MATCHER
          </div>
          <h1 className="font-mono-board text-3xl md:text-4xl text-board-amber tracking-tight">
            JOB MATCH BOARD
          </h1>
          <p className="font-sans-board text-sm text-board-slate mt-2">
            Upload your CV to dynamically parse your skills and match live job listings.
          </p>
        </div>

        {/* Upload Button */}
        <div>
          <label className="cursor-pointer inline-block bg-board-slate text-board-bg px-5 py-2.5 text-sm font-mono-board font-semibold hover:bg-board-amber hover:text-black transition-colors rounded">
            {uploading ? "PARSING RESUME..." : "UPLOAD CV (.PDF)"}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 p-4 border border-board-red/40 bg-board-red/10 text-board-red text-xs font-mono-board">
          {error}
        </div>
      )}

      {/* Extracted Skills Section */}
      {extractedSkills.length > 0 && (
        <div className="mb-6 p-4 border border-board-amber/30 bg-board-amber/5 flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1">
            <div className="text-xs font-mono-board text-board-amber mb-2">
              EXTRACTED SKILLS ({extractedSkills.length}):
            </div>
            <div className="flex flex-wrap gap-2">
              {extractedSkills.map((skill) => (
                <span
                  key={skill}
                  className="text-xs px-2.5 py-1 bg-board-amber/10 text-board-amber border border-board-amber/20 rounded"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={clearCV}
            className="text-xs font-mono-board text-board-slate hover:text-board-red underline self-start md:self-auto cursor-pointer"
          >
            [ CLEAR / UPLOAD NEW ]
          </button>
        </div>
      )}

      {/* Stats Summary (Active only after upload) */}
      {extractedSkills.length > 0 && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="border border-board-line p-4 bg-board-bg">
            <div className="text-2xl font-mono-board text-board-amber">
              {filteredJobs.length}
            </div>
            <div className="text-xs font-mono-board text-board-slate">
              MATCHED LISTINGS
            </div>
          </div>
          <div className="border border-board-line p-4 bg-board-bg">
            <div className="text-2xl font-mono-board text-board-amber">
              {avgMatchScore}%
            </div>
            <div className="text-xs font-mono-board text-board-slate">
              AVERAGE MATCH SCORE
            </div>
          </div>
        </div>
      )}

      {/* Filter Bar for Uploaded Results */}
      {extractedSkills.length > 0 && (
        <div className="mb-4 flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Search within matched jobs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3 py-2 text-sm bg-board-bg border border-board-line text-board-slate focus:outline-none focus:border-board-amber"
          />
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="px-3 py-2 text-sm bg-board-bg border border-board-line text-board-slate focus:outline-none focus:border-board-amber"
          >
            <option value={0}>All Match Scores</option>
            <option value={0.5}>50%+ Match</option>
            <option value={0.75}>75%+ Match</option>
            <option value={1.0}>100% Match Only</option>
          </select>
        </div>
      )}

      {/* Main Results / Empty State Container */}
      <div className="border border-board-line bg-board-bg board-texture">
        {/* State 1: No CV uploaded yet */}
        {!uploading && extractedSkills.length === 0 && (
          <div className="px-6 py-20 text-center flex flex-col items-center justify-center">
            <div className="w-12 h-12 mb-4 text-board-slate opacity-40">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="font-mono-board text-lg text-board-amber mb-1">
              NO RESUME LOADED
            </h3>
            <p className="font-sans-board text-sm text-board-slate max-w-sm">
              Please upload a PDF resume using the button above to discover matching jobs tailored to your skills.
            </p>
          </div>
        )}

        {/* State 2: Uploading / Processing */}
        {uploading && (
          <div className="px-5 py-20 text-center font-mono-board text-sm text-board-slate animate-pulse">
            EXTRACTING SKILLS & SCORING LIVE POSTINGS...
          </div>
        )}

        {/* State 3: CV Uploaded, but 0 matched jobs */}
        {!uploading && extractedSkills.length > 0 && filteredJobs.length === 0 && (
          <div className="px-5 py-12 text-center font-mono-board text-sm text-board-slate">
            NO LISTINGS MATCH THESE FILTER CRITERIA
          </div>
        )}

        {/* State 4: Display Matched Jobs */}
        {!uploading &&
          extractedSkills.length > 0 &&
          filteredJobs.map((job, i) => (
            <JobRow key={job.id} job={job} index={i} />
          ))}
      </div>

      <footer className="mt-6 font-mono-board text-[11px] text-board-slate text-center">
        SOURCES: ADZUNA · REMOTEOK · JOBICY · ARBEITNOW
      </footer>
    </main>
  );
}