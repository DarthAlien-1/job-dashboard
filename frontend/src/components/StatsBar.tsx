import type { Stats } from "@/lib/api";

export default function StatsBar({ stats }: { stats: Stats | null }) {
  const items = [
    { label: "LISTINGS", value: stats ? stats.total_jobs : "—" },
    {
      label: "AVG MATCH",
      value: stats ? `${Math.round(stats.average_match_score * 100)}%` : "—",
    },
    { label: "SOURCES", value: stats ? stats.sources.length : "—" },
  ];

  return (
    <div className="flex flex-wrap gap-px bg-board-line border border-board-line">
      {items.map((item) => (
        <div
          key={item.label}
          className="flex-1 min-w-[140px] bg-board-panel px-5 py-4"
        >
          <div className="font-mono-board text-2xl md:text-3xl text-board-amber tabular-nums">
            {item.value}
          </div>
          <div className="font-mono-board text-[11px] tracking-[0.15em] text-board-slate mt-1">
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
}
