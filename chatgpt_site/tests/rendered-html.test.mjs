import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("renders the World Cup report viewer shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>世界杯赛前分析平台<\/title>/i);
  assert.match(html, /世界杯赛前分析平台/);
  assert.match(html, /API-Football 状态/);
  assert.match(html, /实时赛程/);
  assert.match(html, /核心决策/);
  assert.match(html, /市场盘口/);
  assert.match(html, /查找报告快照/);
  assert.doesNotMatch(html, /codex-preview|SkeletonPreview|react-loading-skeleton/i);
});

test("ships sanitized report snapshot data", async () => {
  const data = JSON.parse(
    await readFile(new URL("../public/reports.json", import.meta.url), "utf8"),
  );

  assert.ok(Array.isArray(data.reports));
  assert.ok(data.reports.length > 0);
  assert.ok(data.reports.length <= 80);
  for (const report of data.reports) {
    assert.equal(typeof report.match, "string");
    assert.equal(typeof report.content, "string");
    assert.ok(report.content.length > 200);
    assert.doesNotMatch(report.content, /API[_-]?KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|\.env/i);
  }
});
