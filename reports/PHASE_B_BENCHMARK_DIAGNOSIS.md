# Phase B Benchmark Diagnosis

Date: 2026-06-21

## Scope

This diagnosis only analyzes:

- `WORLD_CUP_RANKING_BENCHMARK_REPORT.md`
- `WORLD_CUP_BACKTEST_PORTFOLIOS.md`

No code, ranking logic, recommendation logic, UI, or data files were modified.

## Executive Conclusion

Legacy ROI was higher in the 10-match pilot because `Legacy Value Portfolio` repeatedly selected tail-heavy upside structures. Those portfolios were correctly flagged by Hybrid Guardrails as `Blocked`, but several high-score outcomes made the tail exposure pay off.

The current conclusion is not "Legacy is structurally better." The better diagnosis is:

- Legacy captured aggressive upside better.
- Scenario / Hybrid controlled drawdown better.
- Hybrid currently blocks too much upside instead of separating `uncontrolled tail` from `scenario-supported aggressive upside`.

## Key Metrics

| Metric | Result |
| --- | ---: |
| Valid matches | 10 |
| Legacy ROI | 46.5% |
| Scenario ROI | 18.2% |
| Hybrid ROI | 18.2% |
| Legacy Wins | 3 |
| Scenario Wins | 0 |
| Hybrid Wins | 0 |
| Draws | 7 |
| Legacy Top Guardrail Blocked | 10 / 10 |
| Blocked Legacy Top partial hits | 4 |
| Blocked Legacy Top misses | 6 |

## 1. Was Legacy ROI Lifted By High-Odds Tail Upside?

Yes.

Every Legacy Top was `Legacy Value Portfolio`, and every one was:

- `Shadow Verdict = Disagreement`
- `Guardrail = Blocked`
- Block reason included `Tail-heavy`

The aggregate Legacy profit was `+4648.86` on about `10000` stake. Most of that came from a few high-upside outcomes:

| Match | Legacy ROI | Result |
| --- | ---: | --- |
| England vs Croatia | 518.2% | Legacy Winner |
| Netherlands vs Sweden | 350.6% | Legacy Winner |
| Argentina vs Algeria | 127.5% | Legacy Winner |

Those three matches alone produced about `+9964` profit. The other seven matches together were negative.

This means Legacy's high ROI was driven by a small number of large tail wins, not broad match-by-match consistency.

## 2. How Many Legacy Top Portfolios Were Blocked?

`10 / 10` Legacy Top portfolios were blocked by Hybrid Guardrails.

The repeated block reason was:

`Shadow Disagreement, Tail-heavy, Not default-eligible without explanation`

This is an important signal: the Guardrails did not fail to identify risk. They identified the risk correctly, but the risk paid off in some high-scoring matches.

## 3. Blocked Legacy Top Hit / Miss Split

| Outcome | Count | Matches |
| --- | ---: | --- |
| Partial hit | 4 | Argentina vs Algeria, England vs Croatia, Brazil vs Haiti, Netherlands vs Sweden |
| Miss | 6 | France vs Senegal, Portugal vs Congo DR, Canada vs Qatar, Scotland vs Morocco, Germany vs Ivory Coast, Ecuador vs Curaçao |

Blocked Legacy Top missed more often than it hit, but the winning tails were large enough to dominate aggregate ROI.

## 4. Sustainable Edge Or Tail Luck?

Current evidence points to tail-driven upside, not proven sustainable edge.

Reasons:

- Hit rate profile is weak: 4 partial hits, 6 misses.
- Legacy required very large wins to offset frequent full losses.
- Two high-scoring games, England vs Croatia and Netherlands vs Sweden, explain most of the ROI gap.
- Legacy had materially worse max drawdown in almost every non-winning case.
- The sample is only 10 matches, too small to treat tail-hit frequency as stable.

However, this should not be dismissed as pure noise. Legacy may be detecting a real class of upside opportunity: high-score games where correct-score or aggressive return exposure is underweighted by Scenario / Hybrid.

## 5. Are Scenario / Hybrid Too Conservative?

Yes, for high-score games.

Scenario and Hybrid avoided the worst tail losses, but they also failed to retain enough upside in:

- England vs Croatia, final score `4:2`
- Netherlands vs Sweden, final score `5:1`
- Argentina vs Algeria, final score `3:0`

Scenario / Hybrid generally selected `Recommended Blend Portfolio` or `Direction + Return Portfolio`, which produced steadier but capped outcomes. That was safer, but it missed major upside where the match actually entered a high-score path.

This suggests Scenario / Hybrid should not fully suppress aggressive upside. They should require it to be scenario-supported.

## 6. Is Hybrid Penalizing Tail-Heavy Too Much?

Yes, in its current pilot form.

The issue is not that Hybrid flags tail risk. That part is correct. The issue is that Hybrid treats nearly all tail-heavy Legacy Top cases as default-ineligible, even when the match type is:

- high-score sample
- strong favorite pressure
- deep handicap
- market-implied aggressive path

In those contexts, aggressive return exposure may be justified as a controlled sleeve, not as the whole portfolio.

## 7. Should Hybrid Keep Some Aggressive Upside?

Yes.

Hybrid should distinguish three categories:

| Category | Treatment |
| --- | --- |
| Uncontrolled Tail | Block from default recommendation |
| Scenario-Supported Aggressive Upside | Allow as capped sleeve |
| Core Main Scenario Return | Eligible for main ranking weight |

Suggested next design direction:

- Do not let tail-heavy portfolios become default rank 1 without explanation.
- But allow `Aggressive Upside Sleeve` when:
  - Scenario supports high-score or deep-cover path.
  - Tail exposure is capped.
  - Direction Asset remains present.
  - Portfolio still covers Main Scenario.
  - Guardrail reason says `Aggressive but scenario-supported`, not simply `Blocked`.

## Match Diagnosis

| Match | Legacy Top Guardrail | Legacy ROI | Scenario ROI | Diagnosis |
| --- | --- | ---: | ---: | --- |
| France vs Senegal | Blocked | -100.0% | 83.4% | Guardrail helped; Legacy tail missed. |
| Argentina vs Algeria | Blocked | 127.5% | 104.9% | Legacy upside added value, but drawdown was much larger. |
| Portugal vs Congo DR | Blocked | -100.0% | -100.0% | All systems failed; no edge proven. |
| England vs Croatia | Blocked | 518.2% | 73.5% | Legacy tail hit extremely hard; Scenario / Hybrid too conservative. |
| Canada vs Qatar | Blocked | -100.0% | 27.4% | Guardrail helped; Legacy tail missed despite high-score final. |
| Scotland vs Morocco | Blocked | -100.0% | -20.5% | Guardrail helped; Legacy tail missed. |
| Brazil vs Haiti | Blocked | 68.5% | 72.9% | Scenario / Hybrid slightly better with lower drawdown. |
| Netherlands vs Sweden | Blocked | 350.6% | 83.1% | Legacy tail captured 5:1 upside; Scenario / Hybrid too conservative. |
| Germany vs Ivory Coast | Blocked | -100.0% | -42.8% | Guardrail helped; Legacy tail missed. |
| Ecuador vs Curaçao | Blocked | -100.0% | -100.0% | All systems failed; no edge proven. |

## Diagnosis Of The Ranking Logic

Legacy has one useful behavior:

- It does not ignore aggressive upside.

Legacy has one major risk:

- It allows tail-heavy portfolios to become rank 1 too easily.

Scenario / Hybrid have one useful behavior:

- They prevent tail-heavy portfolios from becoming default recommendations.

Scenario / Hybrid have one major risk:

- They currently suppress too much upside in high-score paths.

## Recommended Adjustment Before Phase C

Do not promote Legacy as-is.

Do not promote current Hybrid as-is.

Before Phase C full benchmark, design a Hybrid v0.2 diagnostic rule:

- Keep `Blocked` for uncontrolled tail-heavy portfolios.
- Add `Aggressive Upside Candidate` for high-score/deep-cover scenarios.
- Cap aggressive upside exposure rather than fully excluding it.
- Benchmark three separate buckets:
  - Core Scenario Portfolio
  - Scenario + Aggressive Upside Sleeve
  - Legacy Tail-Heavy Portfolio

This would answer the real question:

Can Hybrid keep Scenario's drawdown control while recovering part of Legacy's high-score upside?

## Final Verdict

Phase B does not prove Legacy is better.

It proves the current Hybrid is too binary:

- It correctly identifies tail-heavy risk.
- It over-blocks aggressive upside.
- It needs a controlled upside sleeve before any production replacement decision.

