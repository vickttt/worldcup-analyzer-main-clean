"use client";

import { useEffect, useMemo, useState } from "react";

type ReportItem = {
  id: string;
  file: string;
  match: string;
  home: string;
  away: string;
  generatedDate: string;
  generatedTime: string;
  heading: string;
  content: string;
};

type ReportPayload = {
  generatedAt: string;
  source: string;
  reports: ReportItem[];
};

type Fixture = {
  fixture_id: number;
  home_team: { id?: number; name: string; logo?: string };
  away_team: { id?: number; name: string; logo?: string };
  kickoff_utc: string;
  league_name: string;
  round: string;
  venue_name: string;
  venue_city: string;
  status: string;
  status_text: string;
  score?: { home: number | null; away: number | null } | null;
};

type ApiSchedule = {
  source?: string;
  fetchedAt?: string;
  fixtures?: Fixture[];
  error?: string;
  hint?: string;
};

type ApiFixtureData = {
  source?: string;
  fetchedAt?: string;
  fixture?: Fixture | null;
  markets?: {
    matchWinner?: unknown[];
    asianHandicap?: unknown[];
    overUnder?: unknown[];
    correctScore?: unknown[];
  };
  team?: {
    injuries?: unknown[];
    lineups?: unknown[];
  };
  warnings?: unknown[];
  error?: string;
  hint?: string;
};

type MarketRow = {
  bookmaker: string;
  bet: string;
  selection: string;
  odds: string;
  extra: string;
};

const marketTitles: Record<keyof NonNullable<ApiFixtureData["markets"]>, string> = {
  matchWinner: "胜平负",
  asianHandicap: "亚洲让球",
  overUnder: "大小球",
  correctScore: "波胆",
};

function extractValue(content: string, patterns: RegExp[]) {
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match?.[1]) return match[1].trim();
  }
  return "暂无";
}

function reportMetrics(report: ReportItem) {
  return [
    {
      label: "主方向",
      value: extractValue(report.content, [
        /主方向[:：|]\s*([^\n|]+)/i,
        /比赛主方向[:：|]\s*([^\n|]+)/i,
        /主投注项[:：|]\s*([^\n|]+)/i,
      ]),
    },
    {
      label: "投资分",
      value: extractValue(report.content, [
        /投资分[:：|]\s*([0-9]+(?:\s*\/\s*100)?)/i,
        /Investment Score[:：|]\s*([0-9]+(?:\s*\/\s*100)?)/i,
      ]),
    },
    {
      label: "推荐金额",
      value: extractValue(report.content, [
        /推荐金额[:：|]\s*([^。\n|]+)/i,
        /推荐资金[:：|]\s*([^。\n|]+)/i,
      ]),
    },
    {
      label: "风险指数",
      value: extractValue(report.content, [
        /风险指数[:：|]\s*([^。\n|]+)/i,
        /RSI[:：|]\s*([^。\n|]+)/i,
      ]),
    },
  ];
}

function localKickoff(value?: string) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("zh-CN", {
      timeZone: "Asia/Shanghai",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function scoreText(fixture: Fixture) {
  if (!fixture.score || fixture.score.home == null || fixture.score.away == null) {
    return fixture.status_text || "未开始";
  }
  return `${fixture.score.home} - ${fixture.score.away}`;
}

function flattenMarkets(items?: unknown[], limit = 8): MarketRow[] {
  const rows: MarketRow[] = [];
  for (const item of (items ?? []) as any[]) {
    for (const bookmaker of item?.bookmakers ?? []) {
      for (const bet of bookmaker?.bets ?? []) {
        for (const value of bet?.values ?? []) {
          rows.push({
            bookmaker: bookmaker?.name ?? "-",
            bet: bet?.name ?? "-",
            selection: value?.value ?? "-",
            odds: value?.odd ?? "-",
            extra: value?.handicap || value?.line || "",
          });
          if (rows.length >= limit) return rows;
        }
      }
    }
  }
  return rows;
}

function markdownBlocks(markdown: string) {
  const lines = markdown.split(/\r?\n/);
  const blocks: { type: "table" | "line"; lines: string[] }[] = [];
  let table: string[] = [];

  for (const line of lines) {
    if (/^\s*\|.*\|\s*$/.test(line)) {
      table.push(line);
      continue;
    }
    if (table.length) {
      blocks.push({ type: "table", lines: table });
      table = [];
    }
    blocks.push({ type: "line", lines: [line] });
  }
  if (table.length) blocks.push({ type: "table", lines: table });
  return blocks;
}

function renderInline(text: string) {
  return text
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .trim();
}

function MarkdownView({ content }: { content: string }) {
  return (
    <div className="markdown-view">
      {markdownBlocks(content).map((block, index) => {
        if (block.type === "table") {
          const rows = block.lines
            .map((line) =>
              line
                .trim()
                .replace(/^\|/, "")
                .replace(/\|$/, "")
                .split("|")
                .map((cell) => renderInline(cell)),
            )
            .filter((row) => !row.every((cell) => /^:?-{3,}:?$/.test(cell)));
          if (!rows.length) return null;
          const [head, ...body] = rows;
          return (
            <div className="table-wrap" key={`table-${index}`}>
              <table>
                <thead>
                  <tr>
                    {head.map((cell, cellIndex) => (
                      <th key={cellIndex}>{cell}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {body.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        const line = block.lines[0];
        const text = renderInline(line);
        if (!text) return null;
        if (text.startsWith("### ")) return <h3 key={index}>{text.slice(4)}</h3>;
        if (text.startsWith("## ")) return <h2 key={index}>{text.slice(3)}</h2>;
        if (text.startsWith("# ")) return <h1 key={index}>{text.slice(2)}</h1>;
        if (/^[-*]\s+/.test(text)) return <li key={index}>{text.replace(/^[-*]\s+/, "")}</li>;
        return <p key={index}>{text}</p>;
      })}
    </div>
  );
}

function MarketTable({ title, rows }: { title: string; rows: MarketRow[] }) {
  return (
    <section className="market-card">
      <h3>{title}</h3>
      {rows.length ? (
        <div className="table-wrap compact">
          <table>
            <thead>
              <tr>
                <th>公司</th>
                <th>盘口</th>
                <th>选择</th>
                <th>赔率</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.bookmaker}-${row.bet}-${row.selection}-${index}`}>
                  <td>{row.bookmaker}</td>
                  <td>{row.extra || row.bet}</td>
                  <td>{row.selection}</td>
                  <td>{row.odds}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="muted">该市场暂未返回数据。</p>
      )}
    </section>
  );
}

export default function Home() {
  const [payload, setPayload] = useState<ReportPayload | null>(null);
  const [schedule, setSchedule] = useState<ApiSchedule | null>(null);
  const [fixtureData, setFixtureData] = useState<ApiFixtureData | null>(null);
  const [selectedId, setSelectedId] = useState<string>("");
  const [selectedFixtureId, setSelectedFixtureId] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"core" | "market" | "source">("core");

  useEffect(() => {
    fetch("/reports.json")
      .then((response) => response.json())
      .then((data: ReportPayload) => {
        setPayload(data);
        setSelectedId(data.reports[0]?.id ?? "");
      })
      .catch(() => setPayload({ generatedAt: "", source: "", reports: [] }));

    fetch("/api/api-football?mode=schedule")
      .then(async (response) => {
        const data = (await response.json()) as ApiSchedule;
        if (!response.ok) throw data;
        return data;
      })
      .then((data) => {
        setSchedule(data);
        setSelectedFixtureId(data.fixtures?.[0]?.fixture_id ?? null);
      })
      .catch((error) => setSchedule({ error: error?.error || "API-Football 赛程加载失败。", hint: error?.hint }));
  }, []);

  useEffect(() => {
    if (!selectedFixtureId) return;
    setFixtureData(null);
    fetch(`/api/api-football?mode=fixture&fixture=${selectedFixtureId}`)
      .then(async (response) => {
        const data = (await response.json()) as ApiFixtureData;
        if (!response.ok) throw data;
        return data;
      })
      .then(setFixtureData)
      .catch((error) =>
        setFixtureData({
          error: error?.error || "API-Football 比赛详情加载失败。",
          hint: error?.hint,
        }),
      );
  }, [selectedFixtureId]);

  const reports = payload?.reports ?? [];
  const fixtures = schedule?.fixtures ?? [];
  const selectedFixture = fixtures.find((fixture) => fixture.fixture_id === selectedFixtureId) ?? fixtures[0];
  const filteredReports = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return reports;
    return reports.filter((report) =>
      [report.match, report.home, report.away, report.heading]
        .join(" ")
        .toLowerCase()
        .includes(normalized),
    );
  }, [query, reports]);

  const selectedReport =
    reports.find((report) => report.id === selectedId) ?? filteredReports[0] ?? reports[0];

  const marketRows = {
    matchWinner: flattenMarkets(fixtureData?.markets?.matchWinner, 10),
    asianHandicap: flattenMarkets(fixtureData?.markets?.asianHandicap, 10),
    overUnder: flattenMarkets(fixtureData?.markets?.overUnder, 10),
    correctScore: flattenMarkets(fixtureData?.markets?.correctScore, 10),
  };

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">World Cup Analyzer</p>
          <h1>世界杯赛前分析平台</h1>
          <p className="hero-copy">
            chatgpt.site 版本保留本地页面的“核心决策 / 市场盘口 / 数据来源”阅读流，
            并由站点后端直接调用 API-Football 获取赛程和盘口。Python 模型计算仍以本地
            Streamlit 生成的报告快照为准。
          </p>
        </div>
        <div className="hero-panel">
          <span>API-Football 状态</span>
          <strong>{schedule?.error ? "待配置" : fixtures.length || "..."}</strong>
          <small>{schedule?.error ? schedule.error : `实时赛程 ${fixtures.length || 0} 场`}</small>
        </div>
      </section>

      {schedule?.error && (
        <section className="notice">
          <strong>远端 API 暂未可用：</strong>
          {schedule.error}
          {schedule.hint ? ` ${schedule.hint}` : ""}
        </section>
      )}

      <section className="live-layout">
        <aside className="live-panel">
          <div className="panel-heading">
            <h2>实时赛程</h2>
            <span>{schedule?.source || "API-Football"}</span>
          </div>
          <div className="fixture-list">
            {fixtures.slice(0, 24).map((fixture) => (
              <button
                className={fixture.fixture_id === selectedFixtureId ? "active" : ""}
                key={fixture.fixture_id}
                onClick={() => setSelectedFixtureId(fixture.fixture_id)}
              >
                <strong>
                  {fixture.home_team.name} vs {fixture.away_team.name}
                </strong>
                <span>
                  {localKickoff(fixture.kickoff_utc)} · {scoreText(fixture)}
                </span>
              </button>
            ))}
            {!fixtures.length && <p className="empty">等待 API-Football 返回赛程。</p>}
          </div>
        </aside>

        <section className="fixture-panel">
          <div className="match-banner">
            <div>
              <p className="eyebrow">当前比赛</p>
              <h2>
                {selectedFixture
                  ? `${selectedFixture.home_team.name} vs ${selectedFixture.away_team.name}`
                  : selectedReport?.match || "暂无比赛"}
              </h2>
              <p>
                {selectedFixture
                  ? `${localKickoff(selectedFixture.kickoff_utc)} · ${selectedFixture.round || "世界杯"}`
                  : "使用报告快照展示。"}
              </p>
            </div>
            <div className="banner-meta">
              <span>场地</span>
              <strong>{selectedFixture?.venue_name || "待确认"}</strong>
              <small>{selectedFixture?.venue_city || "城市待确认"}</small>
            </div>
          </div>

          <nav className="tabs" aria-label="页面分区">
            {[
              ["core", "核心决策"],
              ["market", "市场盘口"],
              ["source", "数据来源"],
            ].map(([key, label]) => (
              <button
                className={activeTab === key ? "active" : ""}
                key={key}
                onClick={() => setActiveTab(key as typeof activeTab)}
              >
                {label}
              </button>
            ))}
          </nav>

          {activeTab === "core" && selectedReport && (
            <>
              <div className="metric-grid">
                {reportMetrics(selectedReport).map((metric) => (
                  <div className="metric-card" key={metric.label}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                  </div>
                ))}
              </div>
              <div className="report-header compact-header">
                <div>
                  <p className="eyebrow">报告快照</p>
                  <h2>{selectedReport.match}</h2>
                  <p>
                    快照时间：{selectedReport.generatedDate} {selectedReport.generatedTime}
                  </p>
                </div>
              </div>
              <MarkdownView content={selectedReport.content} />
            </>
          )}

          {activeTab === "market" && (
            <>
              {fixtureData?.error && (
                <section className="notice soft">
                  <strong>盘口详情暂不可用：</strong>
                  {fixtureData.error}
                  {fixtureData.hint ? ` ${fixtureData.hint}` : ""}
                </section>
              )}
              <div className="market-grid">
                {(Object.keys(marketRows) as Array<keyof typeof marketRows>).map((key) => (
                  <MarketTable key={key} title={marketTitles[key]} rows={marketRows[key]} />
                ))}
              </div>
            </>
          )}

          {activeTab === "source" && (
            <section className="source-panel">
              <h2>数据来源</h2>
              <p>实时数据：由 chatgpt.site 后端 API 路由调用 API-Football。</p>
              <p>模型分析：来自本地 Streamlit 已生成的赛前 Markdown 报告快照。</p>
              <p>最新 API 拉取时间：{fixtureData?.fetchedAt || schedule?.fetchedAt || "暂无"}</p>
              <p>报告快照生成时间：{payload?.generatedAt || "暂无"}</p>
              <p>说明：远端站点不运行 Python/Streamlit 模型，不会在浏览器端暴露 API key。</p>
            </section>
          )}
        </section>

        <aside className="report-list">
          <label htmlFor="report-search">查找报告快照</label>
          <input
            id="report-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="输入球队名，例如 Brazil"
          />
          <div className="list-items">
            {filteredReports.map((report) => (
              <button
                className={report.id === selectedReport?.id ? "active" : ""}
                key={report.id}
                onClick={() => setSelectedId(report.id)}
              >
                <strong>{report.match}</strong>
                <span>
                  {report.generatedDate} {report.generatedTime}
                </span>
              </button>
            ))}
            {!filteredReports.length && <p className="empty">没有匹配的报告。</p>}
          </div>
        </aside>
      </section>
    </main>
  );
}
