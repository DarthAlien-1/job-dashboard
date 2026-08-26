export interface Posting {
  id: number;
  title: string;
  company: string | null;
  location: string | null;
  description: string | null;
  url: string | null;
  posted_date: string | null;
  source: string | null;
  match_score: number;
  matched_skills: string | null;
}

export interface Stats {
  total_jobs: number;
  average_match_score: number;
  sources: string[];
}

const API_BASE = "http://localhost:8000";

export async function fetchJobs(params: {
  min_score?: number;
  source?: string;
  search?: string;
}): Promise<Posting[]> {
  const query = new URLSearchParams();
  if (params.min_score) query.set("min_score", String(params.min_score));
  if (params.source) query.set("source", params.source);
  if (params.search) query.set("search", params.search);

  const res = await fetch(`${API_BASE}/api/jobs?${query.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function uploadCV(file: File): Promise<{ extracted_skills: string[], jobs: Posting[] }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/match-cv`, {
    method: "POST",
    body: formData,
  });
  
  if (!res.ok) throw new Error("Failed to upload CV");
  return res.json();
}
