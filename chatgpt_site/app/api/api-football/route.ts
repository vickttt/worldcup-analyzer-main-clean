const API_BASE = "https://v3.football.api-sports.io";
const WORLD_CUP_LEAGUE_ID = "1";
const WORLD_CUP_SEASON = "2026";
const MATCH_WINNER_BET_ID = "1";
const ASIAN_HANDICAP_BET_ID = "4";
const OVER_UNDER_BET_ID = "5";
const CORRECT_SCORE_BET_ID = "10";

type ApiFootballResponse = {
  response?: unknown;
  errors?: unknown;
  results?: number;
};

export const dynamic = "force-dynamic";

function apiKey() {
  return process.env.API_FOOTBALL_KEY || process.env.api_football_key || "";
}

function errorText(errors: unknown) {
  if (!errors) return "";
  if (Array.isArray(errors)) return errors.filter(Boolean).join("; ");
  if (typeof errors === "object") return Object.values(errors as Record<string, unknown>).filter(Boolean).join("; ");
  return String(errors);
}

function normalizeFixture(item: any) {
  const fixture = item?.fixture ?? {};
  const teams = item?.teams ?? {};
  const league = item?.league ?? {};
  const venue = fixture?.venue ?? {};
  const status = fixture?.status ?? {};
  const goals = item?.goals ?? {};
  return {
    fixture_id: fixture.id,
    home_team: {
      id: teams.home?.id,
      name: teams.home?.name,
      logo: teams.home?.logo,
    },
    away_team: {
      id: teams.away?.id,
      name: teams.away?.name,
      logo: teams.away?.logo,
    },
    kickoff_utc: fixture.date,
    league_name: `${league.name || "World Cup"} ${league.season || WORLD_CUP_SEASON}`,
    round: league.round || "",
    venue_name: venue.name || "",
    venue_city: venue.city || "",
    status: status.short || "NS",
    status_text: status.long || "未开始",
    score: goals.home != null || goals.away != null ? { home: goals.home, away: goals.away } : null,
    source: "API-Football",
  };
}

async function requestApi(path: string, params: Record<string, string>) {
  const key = apiKey();
  if (!key) {
    return {
      ok: false,
      status: 401,
      body: {
        error: "API_FOOTBALL_KEY 未配置到 Sites 运行环境。",
        hint: "请在 chatgpt.site / Sites 环境变量中添加 API_FOOTBALL_KEY。",
      },
    };
  }

  const url = new URL(`${API_BASE}${path}`);
  for (const [name, value] of Object.entries(params)) {
    if (value) url.searchParams.set(name, value);
  }

  const response = await fetch(url, {
    cache: "no-store",
    headers: {
      "x-apisports-key": key,
      Accept: "application/json",
    },
  });
  const data = (await response.json()) as ApiFootballResponse;
  const apiError = errorText(data.errors);
  if (!response.ok || apiError) {
    return {
      ok: false,
      status: response.ok ? 502 : response.status || 502,
      body: { error: apiError || `API-Football HTTP ${response.status}` },
    };
  }
  return { ok: true, status: 200, body: data.response ?? [] };
}

async function schedule() {
  const result = await requestApi("/fixtures", {
    league: WORLD_CUP_LEAGUE_ID,
    season: WORLD_CUP_SEASON,
  });
  if (!result.ok) return Response.json(result.body, { status: result.status });
  const fixtures = (result.body as any[])
    .map(normalizeFixture)
    .filter((fixture) => fixture.fixture_id && fixture.home_team.name && fixture.away_team.name)
    .sort((a, b) => String(a.kickoff_utc || "").localeCompare(String(b.kickoff_utc || "")));
  return Response.json({
    source: "API-Football",
    fetchedAt: new Date().toISOString(),
    fixtures,
  });
}

async function fixtureMarkets(fixtureId: string) {
  if (!fixtureId) {
    return Response.json({ error: "fixture 参数缺失。" }, { status: 400 });
  }

  const [fixture, matchWinner, asianHandicap, overUnder, correctScore, injuries, lineups] = await Promise.all([
    requestApi("/fixtures", { id: fixtureId }),
    requestApi("/odds", { fixture: fixtureId, bet: MATCH_WINNER_BET_ID }),
    requestApi("/odds", { fixture: fixtureId, bet: ASIAN_HANDICAP_BET_ID }),
    requestApi("/odds", { fixture: fixtureId, bet: OVER_UNDER_BET_ID }),
    requestApi("/odds", { fixture: fixtureId, bet: CORRECT_SCORE_BET_ID }),
    requestApi("/injuries", { fixture: fixtureId }),
    requestApi("/fixtures/lineups", { fixture: fixtureId }),
  ]);

  const firstError = [fixture, matchWinner, asianHandicap, overUnder, correctScore, injuries, lineups].find((item) => !item.ok);
  if (firstError && firstError.status === 401) {
    return Response.json(firstError.body, { status: firstError.status });
  }

  const rawFixture = fixture.ok && Array.isArray(fixture.body) ? fixture.body[0] : null;
  return Response.json({
    source: "API-Football",
    fetchedAt: new Date().toISOString(),
    fixture: rawFixture ? normalizeFixture(rawFixture) : null,
    markets: {
      matchWinner: matchWinner.ok ? matchWinner.body : [],
      asianHandicap: asianHandicap.ok ? asianHandicap.body : [],
      overUnder: overUnder.ok ? overUnder.body : [],
      correctScore: correctScore.ok ? correctScore.body : [],
    },
    team: {
      injuries: injuries.ok ? injuries.body : [],
      lineups: lineups.ok ? lineups.body : [],
    },
    warnings: [fixture, matchWinner, asianHandicap, overUnder, correctScore, injuries, lineups]
      .filter((item) => !item.ok)
      .map((item) => item.body),
  });
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const mode = url.searchParams.get("mode") || "schedule";
  if (mode === "schedule") return schedule();
  if (mode === "fixture") return fixtureMarkets(url.searchParams.get("fixture") || "");
  return Response.json({ error: "未知 API-Football 模式。" }, { status: 400 });
}
