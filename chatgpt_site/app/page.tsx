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

function extractValue(content: string, patterns: RegExp[]) {
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match?.[1]) {
      return match[1].trim();
    }
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
  if (table.length) {
    blocks.push({ type: "table", lines: table });
  }
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

export default function Home() {
  const [payload, setPayload] = useState<ReportPayload | null>(null);
  const [selectedId, setSelectedId] = useState<string>("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch("/reports.json")
      .then((response) => response.json())
      .then((data: ReportPayload) => {
        setPayload(data);
        setSelectedId(data.reports[0]?.id ?? "");
      })
      .catch(() => setPayload({ generatedAt: "", source: "", reports: [] }));
  }, []);

  const reports = payload?.reports ?? [];
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

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">World Cup Analyzer</p>
          <h1>世界杯赛前分析平台</h1>
          <p className="hero-copy">
            chatgpt.site 只读版，展示本地 Streamlit 已生成的赛前报告快照。
            模型计算、API 刷新和本地数据维护仍保留在本地应用中。
          </p>
        </div>
        <div className="hero-panel">
          <span>报告数</span>
          <strong>{reports.length || "..."}</strong>
          <small>最近快照：{payload?.generatedAt || "加载中"}</small>
        </div>
      </section>

      <section className="workspace">
        <aside className="report-list">
          <label htmlFor="report-search">查找比赛</label>
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

        <section className="report-panel">
          {selectedReport ? (
            <>
              <div className="report-header">
                <div>
                  <p className="eyebrow">当前报告</p>
                  <h2>{selectedReport.match}</h2>
                  <p>
                    快照时间：{selectedReport.generatedDate} {selectedReport.generatedTime}
                  </p>
                </div>
              </div>

              <div className="metric-grid">
                {reportMetrics(selectedReport).map((metric) => (
                  <div className="metric-card" key={metric.label}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                  </div>
                ))}
              </div>

              <MarkdownView content={selectedReport.content} />
            </>
          ) : (
            <div className="empty-state">正在加载报告快照。</div>
          )}
        </section>
      </section>
    </main>
  );
}
