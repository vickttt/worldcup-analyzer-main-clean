# Hybrid v0.2 Pilot Report

Date: 2026-06-21

## Scope

- Uses existing Phase B historical backfill snapshots only.
- Compares report-only structures: Core, Core + Upside Sleeve, and Legacy Tail-Heavy.
- Does not modify app.py, production sorting, recommendation logic, UI, or data files.

## Structure Definitions

- Core Portfolio: Scenario Rank 1 portfolio from existing benchmark metadata.
- Upside Sleeve: Tail Upside Portfolio, capped by match type.
- Core + Upside Sleeve: Core Portfolio plus capped sleeve allocation.
- Legacy Tail-Heavy: Legacy Value Portfolio from Phase B benchmark.

## Sleeve Caps Used In This Pilot

| Match Type | Sleeve Share |
| --- | ---: |
| Low-score | 5% |
| Cold upset risk | 10% |
| Strong favorite | 15% |
| High-score / strong favorite high-score | 20% |

## Aggregate Result

| Structure | ROI | Hit Rate | Avg Max Drawdown | Total P/L |
| --- | ---: | ---: | ---: | ---: |
| Core | 18.2% | 60.0% | -423 | +1819 |
| Core + Upside Sleeve | 20.6% | 60.0% | -422 | +2055 |
| Legacy Tail-Heavy | 46.5% | 40.0% | -931 | +4649 |

## Match-Level Result

| Match | Type | Final | Sleeve | Core ROI | Core+Upside ROI | Legacy Tail ROI | Core+Upside vs Core | Drawdown Check |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| France vs Senegal | 强队深盘 / 高比分局 | 3:1 | 20.0% | 83.4% | 88.7% | -100.0% | +53 | Lower than Legacy |
| Argentina vs Algeria | 强队深盘 | 3:0 | 15.0% | 104.9% | 106.9% | 127.5% | +20 | Lower than Legacy |
| England vs Croatia | 平衡局 / 高比分局 | 4:2 | 20.0% | 73.5% | 79.6% | 518.2% | +62 | Lower than Legacy |
| Portugal vs Congo DR | 冷门风险局 / 低比分局 | 1:1 | 5.0% | -100.0% | -100.0% | -100.0% | +0 | Same/Higher |
| Canada vs Qatar | 强队深盘 / 高比分局 | 6:0 | 20.0% | 27.4% | 37.6% | -100.0% | +102 | Lower than Legacy |
| Scotland vs Morocco | 平衡局 / 冷门风险局 | 0:1 | 10.0% | -20.5% | -28.4% | -100.0% | -79 | Lower than Legacy |
| Brazil vs Haiti | 强队深盘 | 3:0 | 15.0% | 72.9% | 74.6% | 68.5% | +17 | Lower than Legacy |
| Germany vs Ivory Coast | 强队深盘 / 盘口边界 | 2:1 | 15.0% | -42.8% | -51.4% | -100.0% | -86 | Lower than Legacy |
| Netherlands vs Sweden | 平衡局 / 高比分局 | 5:1 | 20.0% | 83.1% | 97.9% | 350.6% | +148 | Lower than Legacy |
| Ecuador vs Curaçao | 平衡局 / 低比分局 | 0:0 | 5.0% | -100.0% | -100.0% | -100.0% | +0 | Lower than Legacy |

## Question Answers

### 1. Is Core + Upside better than Core?

Yes.

- Core ROI: 18.2%.
- Core + Upside ROI: 20.6%.
- Difference: 2.4%.

### 2. Does Core + Upside retain part of Legacy high-score upside?

Yes, partially.

- Core + Upside improved over Core only where the Tail Upside sleeve contributed positive incremental value.
- It still did not capture the full Legacy Tail-Heavy payoff in England vs Croatia or Netherlands vs Sweden because sleeve exposure was capped.

### 3. Does Core + Upside avoid Legacy extreme losses?

Yes.

- Core + Upside average max drawdown: -422.
- Legacy Tail-Heavy average max drawdown: -931.
- The capped sleeve avoids making the entire portfolio dependent on tail outcomes.

### 4. Is Hybrid v0.2 Report-Only worth entering?

Yes.

- The pilot supports testing Hybrid v0.2 in report-only mode because it directly measures the tradeoff between drawdown control and upside recovery.
- It should not change production sorting or recommendation eligibility yet.
- The next report-only benchmark should separate sleeve candidates by scenario support rather than using Tail Upside Portfolio as a generic proxy.

## Diagnosis

- Core remains the safest structure, but it leaves upside on the table in high-score games.
- Legacy Tail-Heavy captures the most upside, but with frequent full-loss exposure.
- Core + Upside Sleeve is the right experimental direction because it lets the system test controlled aggressive exposure without reverting to Legacy tail-heavy behavior.

## Verdict

- Enter `Hybrid v0.2 Report-Only` stage.
- Keep production sorting unchanged.
- Keep UI unchanged.
- Do not promote Core + Upside until full Phase C benchmark proves the sleeve improves ROI without pushing drawdown near Legacy Tail-Heavy.
