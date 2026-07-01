# Hybrid v0.2 Report-Only Report

Date: 2026-06-21

## Scope

- Reads existing `data/history/backfill/` snapshots only.
- Generates report-only Core, Upside Sleeve, Core + Upside, and Legacy Tail-Heavy comparisons.
- Does not modify `app.py`, production sorting, recommendation logic, UI, score functions, or existing source data.

## Aggregate Result

| Structure | ROI | Hit Rate | Avg Max Drawdown | Total P/L |
| --- | ---: | ---: | ---: | ---: |
| Core Portfolio | 18.2% | 60.0% | -423 | +1819 |
| Core + Upside Portfolio | 20.6% | 60.0% | -422 | +2055 |
| Legacy Tail-Heavy Portfolio | 46.5% | 40.0% | -931 | +4649 |

## Match-Level Report

| Match | Type | Final | Core Portfolio | Upside Sleeve | Sleeve Share | Sleeve Status | Guardrail Status | Core ROI | Core+Upside ROI | Legacy ROI | Core+Upside Max DD | Legacy Max DD |
| --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| France vs Senegal | 强队深盘 / 高比分局 | 3:1 | Recommended Blend Portfolio | Tail Upside Portfolio | 20.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 83.4% | 88.7% | -100.0% | -156 | -1000 |
| Argentina vs Algeria | 强队深盘 | 3:0 | Recommended Blend Portfolio | Tail Upside Portfolio | 15.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 104.9% | 106.9% | 127.5% | -141 | -766 |
| England vs Croatia | 平衡局 / 高比分局 | 4:2 | Recommended Blend Portfolio | Tail Upside Portfolio | 20.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 73.5% | 79.6% | 518.2% | -147 | -903 |
| Portugal vs Congo DR | 冷门风险局 / 低比分局 | 1:1 | Recommended Blend Portfolio | Tail Upside Portfolio | 5.0% | Watch: Small Upside Sleeve | Watch: Small Upside Sleeve | -100.0% | -100.0% | -100.0% | -1000 | -1000 |
| Canada vs Qatar | 强队深盘 / 高比分局 | 6:0 | Recommended Blend Portfolio | Tail Upside Portfolio | 20.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 27.4% | 37.6% | -100.0% | -170 | -1000 |
| Scotland vs Morocco | 平衡局 / 冷门风险局 | 0:1 | Recommended Blend Portfolio | Tail Upside Portfolio | 10.0% | Watch: Small Upside Sleeve | Watch: Small Upside Sleeve | -20.5% | -28.4% | -100.0% | -660 | -1000 |
| Brazil vs Haiti | 强队深盘 | 3:0 | Direction + Return Portfolio | Tail Upside Portfolio | 15.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 72.9% | 74.6% | 68.5% | -95 | -734 |
| Germany vs Ivory Coast | 强队深盘 / 盘口边界 | 2:1 | Recommended Blend Portfolio | Tail Upside Portfolio | 15.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | -42.8% | -51.4% | -100.0% | -670 | -1000 |
| Netherlands vs Sweden | 平衡局 / 高比分局 | 5:1 | Recommended Blend Portfolio | Tail Upside Portfolio | 20.0% | Scenario-Supported Aggressive Upside | Allowed Sleeve | 83.1% | 97.9% | 350.6% | -178 | -908 |
| Ecuador vs Curaçao | 平衡局 / 低比分局 | 0:0 | Recommended Blend Portfolio | Tail Upside Portfolio | 5.0% | Watch: Small Upside Sleeve | Watch: Small Upside Sleeve | -100.0% | -100.0% | -100.0% | -1000 | -1000 |

## Sleeve Reasons

| Match | Sleeve Reason |
| --- | --- |
| France vs Senegal | High-score strong-favorite sample; capped upside sleeve tests scenario-supported aggressive return. |
| Argentina vs Algeria | Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative. |
| England vs Croatia | High-score sample; capped upside sleeve tests recovery of Legacy upside without full tail exposure. |
| Portugal vs Congo DR | Low-score sample; sleeve kept at minimum observation size. |
| Canada vs Qatar | High-score strong-favorite sample; capped upside sleeve tests scenario-supported aggressive return. |
| Scotland vs Morocco | Upset-risk sample; sleeve allowed only as small capped exposure. |
| Brazil vs Haiti | Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative. |
| Germany vs Ivory Coast | Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative. |
| Netherlands vs Sweden | High-score sample; capped upside sleeve tests recovery of Legacy upside without full tail exposure. |
| Ecuador vs Curaçao | Low-score sample; sleeve kept at minimum observation size. |

## Suitable For Upside Sleeve

- France vs Senegal: High-score strong-favorite sample; capped upside sleeve tests scenario-supported aggressive return.
- Argentina vs Algeria: Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative.
- England vs Croatia: High-score sample; capped upside sleeve tests recovery of Legacy upside without full tail exposure.
- Canada vs Qatar: High-score strong-favorite sample; capped upside sleeve tests scenario-supported aggressive return.
- Brazil vs Haiti: Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative.
- Germany vs Ivory Coast: Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative.
- Netherlands vs Sweden: High-score sample; capped upside sleeve tests recovery of Legacy upside without full tail exposure.

## Not Suitable Or Small-Sleeve Only

- Portugal vs Congo DR: Low-score sample; sleeve kept at minimum observation size.
- Ecuador vs Curaçao: Low-score sample; sleeve kept at minimum observation size.

## Required Questions

### Is Core + Upside better than Core?

Yes.

- Core ROI: 18.2%.
- Core + Upside ROI: 20.6%.
- Difference: 2.4%.

### Does Core + Upside reduce Legacy extreme drawdown?

Yes.

- Core + Upside average max drawdown: -422.
- Legacy Tail-Heavy average max drawdown: -931.

### Does Core + Upside recover part of Legacy upside?

Partially. It improves over Core while staying materially below Legacy Tail-Heavy drawdown.

### Should the project enter Visible Diagnostic?

Recommendation: `Enter Visible Diagnostic`.

- Visible Diagnostic should remain observation-only.
- It should not change production sorting, recommendation eligibility, or UI decision logic unless separately approved.
