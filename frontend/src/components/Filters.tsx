interface FiltersProps {
  search: string;
  onSearchChange: (v: string) => void;
  minScore: number;
  onMinScoreChange: (v: number) => void;
  source: string;
  onSourceChange: (v: string) => void;
  sources: string[];
}

export default function Filters({
  search,
  onSearchChange,
  minScore,
  onMinScoreChange,
  source,
  onSourceChange,
  sources,
}: FiltersProps) {
  return (
    <div className="border border-t-0 border-board-line bg-board-panel px-5 py-4 flex flex-wrap items-center gap-6">
      <div className="flex flex-col gap-1 flex-1 min-w-[200px]">
        <label className="font-mono-board text-[11px] tracking-[0.15em] text-board-slate">
          SEARCH
        </label>
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="title or company..."
          className="bg-board-bg border border-board-line px-3 py-2 text-sm text-board-text font-sans-board outline-none focus:border-board-amber transition-colors"
        />
      </div>

      <div className="flex flex-col gap-1 min-w-[220px]">
        <label className="font-mono-board text-[11px] tracking-[0.15em] text-board-slate">
          MIN MATCH — {Math.round(minScore * 100)}%
        </label>
        <input
          type="range"
          min={0}
          max={100}
          value={minScore * 100}
          onChange={(e) => onMinScoreChange(Number(e.target.value) / 100)}
          className="accent-board-amber"
        />
      </div>

      <div className="flex flex-col gap-1 min-w-[160px]">
        <label className="font-mono-board text-[11px] tracking-[0.15em] text-board-slate">
          SOURCE
        </label>
        <select
          value={source}
          onChange={(e) => onSourceChange(e.target.value)}
          className="bg-board-bg border border-board-line px-3 py-2 text-sm text-board-text font-sans-board outline-none focus:border-board-amber transition-colors"
        >
          <option value="">All sources</option>
          {sources.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
