# Operational Dashboard v1

Date: 2026-06-21

Scope: operational overview only. This dashboard does not write code, change system behavior, modify UI, modify recommendation logic, modify data files, create branches, commit, or push.

## 1. 项目当前状态

Current stage:

```text
Development
```

Stage options:

| Stage | Meaning | Current |
| --- | --- | --- |
| Development | Building workflow, automation, reports, and validation structure. | Yes |
| Validation | Running enough completed-match checks to judge ranking quality. | Partial |
| Operation | Stable daily use with validated promotion rules. | No |

Reason:

- Scenario Engine, Recommendation Auditor, Shadow Metadata, Visible Shadow Mode, Portfolio Ranking table slimming, and Post-Match Validation Automation exist.
- But post-match evidence is still limited.
- Only `2 / 5` required validations are available for the first promotion checkpoint.

## 2. 当前验证进度

Post-Match Validation:

```text
2 / 5
```

Current source:

- `POST_MATCH_VALIDATION_REPORT.md`

Status:

- 2 post-match files discovered.
- 2 valid comparisons generated.
- 0 insufficient comparisons.

Promotion status:

```text
Keep Shadow Mode
```

Reason:

- 5 valid post-match validations are required before considering Scenario Guardrails Phase.

## 3. Legacy vs Scenario

Current validated results:

| Metric | Count |
| --- | ---: |
| Legacy Wins | 1 |
| Scenario Wins | 0 |
| Draws | 1 |
| Valid Matches | 2 |

Aggregate ROI:

| Ranking | ROI |
| --- | ---: |
| Legacy Top | 74.8% |
| Scenario Top | 55.8% |

Interpretation:

- Current post-match evidence does not yet prove Scenario Top is better than Legacy Top.
- Scenario Rank remains useful as an observation layer, but not as a replacement.

## 4. Shadow Mode 状态

Current Shadow Mode status:

```text
Active
```

Options:

| Status | Meaning | Current |
| --- | --- | --- |
| Active | Scenario Ranking observes beside Legacy Ranking. | Yes |
| Promoted | Scenario signals affect guardrails or eligibility. | No |
| Deprecated | Shadow Mode is removed or no longer useful. | No |

Current rule:

```text
Legacy Ranking decides.
Scenario Ranking observes.
Post-match validation judges both.
```

## 5. 当前推荐体系

Current recommendation system:

```text
Legacy Official
```

Options:

| System | Meaning | Current |
| --- | --- | --- |
| Legacy Official | Legacy Rank and score remain authoritative. | Yes |
| Scenario Observation | Scenario Rank and Shadow Verdict provide warnings only. | Active as support |
| Scenario Guardrails | Scenario can affect default recommendation eligibility. | No |

Current operating rule:

- Legacy Rank 1 remains the formal recommendation.
- Scenario Rank is displayed for observation.
- Shadow Verdict helps identify disagreement.
- Scenario Rank does not yet change sorting or default recommendation eligibility.

## 6. 最近 5 场比赛摘要

Currently validated post-match matches:

| Match | Final Score | Legacy Top | Scenario Top | Result |
| --- | --- | --- | --- | --- |
| 瑞士 vs 波黑 | 4:1 | 推荐组合（当前最优） | 备选组合4 | Legacy Winner |
| 美国 vs 澳大利亚 | 2:0 | 推荐组合（当前最优） | 推荐组合（当前最优） | Draw |

Recent pre-match / validation context not yet fully post-match validated:

| Match | Status | Note |
| --- | --- | --- |
| Germany vs Ivory Coast | Shadow validation exists | Needs post-match validation if final result is available. |
| Scotland vs Morocco | Shadow validation exists | Needs post-match validation if final result is available. |
| Brazil vs Haiti | Shadow validation exists | Needs post-match validation if final result is available. |

Dashboard limitation:

- The latest 5-match operational view is not complete until 5 valid post-match validation records exist.

## 7. 下一里程碑

Next milestone:

```text
Reach 5 valid post-match validations.
```

Promotion review trigger:

After 5 valid post-match validations, review whether all conditions hold:

- Scenario Top ROI >= Legacy Top ROI.
- Scenario Top wins at least 3 matches or is not worse than Legacy.
- Scenario Top does not have materially larger drawdown.
- Scenario Rank downgrade reasons for Legacy Rank 1 are supported by post-match outcomes.

If satisfied:

```text
Enter Scenario Guardrails Phase
```

If not satisfied:

```text
Keep Shadow Mode
```

## 8. 一句话项目状态

```text
Scenario Layer 已证明有观察价值，但尚未获得足够赛后证据进入 Guardrails。
```

## 9. Current Dashboard Verdict

Verdict:

```text
Keep Shadow Mode
```

Reason:

- Shadow Mode is useful and active.
- Legacy Ranking remains official.
- Scenario Guardrails are not yet justified by post-match evidence.
- The immediate operational priority is not new model work, but collecting 3 more valid post-match validations.
