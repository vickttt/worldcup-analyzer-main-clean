"use client";

import { type ReactNode, useEffect, useMemo, useState } from "react";

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

type ReportSection = {
  title: string;
  raw: string;
};

const marketTitles: Record<keyof NonNullable<ApiFixtureData["markets"]>, string> = {
  matchWinner: "胜平负",
  asianHandicap: "亚洲让球",
  overUnder: "大小球",
  correctScore: "波胆",
};

const reportTabConfig = [
  { id: "decision", label: "重点结论", hint: "先看投注组合、排序、投资分和风险指数。" },
  { id: "scenario", label: "情景与风险", hint: "查看情景概率、结果分布和主要风险路径。" },
  { id: "odds", label: "赔率与盘口", hint: "胜平负、让球、大小球和波胆统一折叠展示。" },
  { id: "team", label: "球队与数据", hint: "伤病、首发、Polymarket 和数据来源说明。" },
  { id: "full", label: "完整报告", hint: "按原报告章节折叠查看全部内容。" },
] as const;

type ReportTabId = (typeof reportTabConfig)[number]["id"];

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
    .replace(/<\/?(details|summary)>/gi, "")
    .trim();
}

function parseDetailLine(line: string) {
  const match = line
    .trim()
    .match(/^<details>\s*<summary>(.*?)<\/summary>\s*([\s\S]*?)\s*<\/details>$/i);
  if (!match) return null;
  return {
    summary: renderInline(match[1]),
    body: renderInline(match[2]),
  };
}

function splitReportSections(content: string): { intro: string; sections: ReportSection[] } {
  const lines = content.split(/\r?\n/);
  const intro: string[] = [];
  const sections: ReportSection[] = [];
  let current: string[] = [];

  const flush = () => {
    if (!current.length) return;
    const firstLine = current[0] ?? "";
    sections.push({
      title: renderInline(firstLine.replace(/^##\s+/, "")),
      raw: current.join("\n").trim(),
    });
    current = [];
  };

  for (const line of lines) {
    if (line.startsWith("## ")) {
      flush();
      current.push(line);
      continue;
    }
    if (current.length) {
      current.push(line);
    } else {
      intro.push(line);
    }
  }
  flush();

  return { intro: intro.join("\n").trim(), sections };
}

function sectionMatches(section: ReportSection, keywords: string[]) {
  const haystack = `${section.title}\n${section.raw}`.toLowerCase();
  return keywords.some((keyword) => haystack.includes(keyword.toLowerCase()));
}

function sectionsByKeywords(sections: ReportSection[], keywords: string[]) {
  return sections.filter((section) => sectionMatches(section, keywords));
}

function sectionBody(section: ReportSection) {
  return section.raw.replace(/^##\s+[^\n]*\n?/, "").trim();
}

function initials(name?: string) {
  const parts = (name || "?").split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
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
        const detail = parseDetailLine(line);
        if (detail) {
          return (
            <details className="markdown-detail" key={index}>
              <summary>{detail.summary}</summary>
              <p>{detail.body}</p>
            </details>
          );
        }
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

function SectionAccordion({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details className="report-accordion" open={defaultOpen}>
      <summary>
        <span>{title}</span>
        <small>{defaultOpen ? "已展开" : "点击展开"}</small>
      </summary>
      <div className="accordion-body">{children}</div>
    </details>
  );
}

function AccordionSections({
  sections,
  emptyText,
  defaultOpenFirst = false,
}: {
  sections: ReportSection[];
  emptyText: string;
  defaultOpenFirst?: boolean;
}) {
  if (!sections.length) {
    return <p className="muted">{emptyText}</p>;
  }
  return (
    <div className="accordion-stack">
      {sections.map((section, index) => (
        <SectionAccordion
          key={`${section.title}-${index}`}
          title={section.title}
          defaultOpen={defaultOpenFirst && index === 0}
        >
          <MarkdownView content={sectionBody(section)} />
        </SectionAccordion>
      ))}
    </div>
  );
}

function ReportTabbedView({ report }: { report: ReportItem }) {
  const [activeReportTab, setActiveReportTab] = useState<ReportTabId>("decision");
  const { intro, sections } = useMemo(() => splitReportSections(report.content), [report.content]);

  const decisionSections = sectionsByKeywords(sections, [
    "最终决策",
    "投资评分",
    "投注组合",
    "组合覆盖结构",
    "风险指数",
    "波胆结构信号",
    "Portfolio Coverage",
    "Execution Layer",
    "我的实盘组合",
  ]);
  const scenarioSections = sectionsByKeywords(sections, [
    "情景",
    "结果分布",
    "进球数观点",
    "风险",
  ]);
  const oddsSections = sectionsByKeywords(sections, [
    "盘口观察",
    "胜平负",
    "Match Winner",
    "亚洲让球",
    "Asian Handicap",
    "大小球",
    "Over/Under",
    "波胆 / Correct Score",
    "赔率",
  ]);
  const teamSections = sectionsByKeywords(sections, [
    "比赛概览",
    "伤病",
    "首发",
    "Polymarket",
    "数据来源",
    "TPB 覆盖说明",
  ]);

  return (
    <section className="report-workspace">
      <div className="report-subtabs" aria-label="报告阅读分区">
        {reportTabConfig.map((tab) => (
          <button
            className={activeReportTab === tab.id ? "active" : ""}
            key={tab.id}
            onClick={() => setActiveReportTab(tab.id)}
          >
            <strong>{tab.label}</strong>
            <span>{tab.hint}</span>
          </button>
        ))}
      </div>

      <div className="report-tab-panel">
        {activeReportTab === "decision" && (
          <MarkdownView content={decisionSections.map((section) => section.raw).join("\n\n") || report.content} />
        )}

        {activeReportTab === "scenario" && (
          <AccordionSections
            sections={scenarioSections}
            emptyText="这份报告暂无独立的情景或风险章节。"
            defaultOpenFirst
          />
        )}

        {activeReportTab === "odds" && (
          <AccordionSections sections={oddsSections} emptyText="这份报告暂无盘口明细章节。" />
        )}

        {activeReportTab === "team" && (
          <AccordionSections
            sections={teamSections}
            emptyText="这份报告暂无球队或外部数据章节。"
            defaultOpenFirst
          />
        )}

        {activeReportTab === "full" && (
          <div className="full-report-stack">
            {intro && (
              <SectionAccordion title="报告标题与摘要" defaultOpen>
                <MarkdownView content={intro} />
              </SectionAccordion>
            )}
            <AccordionSections sections={sections} emptyText="暂无完整报告内容。" />
          </div>
        )}
      </div>
    </section>
  );
}

function TeamIdentity({
  name,
  logo,
  align = "home",
}: {
  name: string;
  logo?: string;
  align?: "home" | "away";
}) {
  return (
    <div className={`team-identity ${align === "away" ? "away" : ""}`}>
      <div className="team-logo-wrap">
        {logo ? <img src={logo} alt={`${name} logo`} /> : <span>{initials(name)}</span>}
      </div>
      <strong>{name}</strong>
    </div>
  );
}

function MarketTable({ title, rows }: { title: string; rows: MarketRow[] }) {
  return (
    <details className="market-accordion">
      <summary>
        <span>{title}</span>
        <small>{rows.length ? `${rows.length} 条盘口` : "暂无数据"}</small>
      </summary>
      <div className="market-accordion-body">
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
      </div>
    </details>
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
  const bannerHomeName = selectedFixture?.home_team.name || selectedReport?.home || "主队";
  const bannerAwayName = selectedFixture?.away_team.name || selectedReport?.away || "客队";

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
            <div className="match-teams">
              <p className="eyebrow">当前比赛</p>
              <div className="team-versus">
                <TeamIdentity name={bannerHomeName} logo={selectedFixture?.home_team.logo} />
                <span className="versus-badge">VS</span>
                <TeamIdentity name={bannerAwayName} logo={selectedFixture?.away_team.logo} align="away" />
              </div>
              <p className="match-context">
                {selectedFixture
                  ? `${localKickoff(selectedFixture.kickoff_utc)} · ${selectedFixture.round || "世界杯"}`
                  : selectedReport?.match || "使用报告快照展示。"}
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
              <ReportTabbedView report={selectedReport} />
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
