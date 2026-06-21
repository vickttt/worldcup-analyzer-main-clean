# My Portfolio Validation Check

Date: 2026-06-21

Scope: inspection only. This check does not modify code, business logic, UI, recommendation logic, ranking, or data files.

## Summary

Current status:

```text
My Portfolio is only partially connected to post-match validation.
```

The post-match validation script can settle a My Portfolio only if it is embedded inside the pre-match snapshot as:

```text
pre_snapshot["my_portfolio"]["items"]
```

But it does not currently read the independently saved files:

```text
data/history/my_portfolios/*.json
```

Therefore,赛前录入并保存到 `data/history/my_portfolios/` 的 My Portfolio is not reliably included in `POST_MATCH_VALIDATION_REPORT.md`.

## 1. 是否读取 `data/history/my_portfolios/*.json`

Result:

```text
No
```

Checked file:

```text
scripts/generate_post_match_validation_report.py
```

Relevant script behavior:

```text
HISTORY_DIR = ROOT / "data/history"
post_paths = sorted(HISTORY_DIR.glob("*_post.json"))
```

The script discovers post-match files from:

```text
data/history/*_post.json
```

It then resolves a pre-match snapshot and reads My Portfolio only from that pre snapshot:

```python
def my_portfolio_strategy(snapshot):
    my_portfolio = snapshot.get("my_portfolio") or {}
    items = my_portfolio.get("items") if isinstance(my_portfolio, dict) else None
```

There is no reference to:

```text
data/history/my_portfolios/
```

or:

```text
my_portfolios/*.json
```

## 2. 当前 `POST_MATCH_VALIDATION_REPORT.md` 是否生成 My Portfolio 结果

Result:

```text
No
```

Current report includes portfolio rows for:

- Legacy Top
- Scenario Top
- Current Recommendation

Current report does not include rows where:

```text
Type = My Portfolio
```

Therefore the current report does not generate My Portfolio-specific:

- Hit Status
- P/L
- ROI
- Validation Result

## 3. 为什么当前没有生成 My Portfolio

The script has this conditional path:

```python
my_strategy = my_portfolio_strategy(pre_snapshot)

if my_strategy:
    selected.append(("My Portfolio", my_strategy))
```

But the two currently validated post-match pre snapshots contain empty embedded My Portfolio data:

| Pre Snapshot | Embedded `my_portfolio.items` |
| --- | ---: |
| `data/history/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json` | 0 |
| `data/history/2026_06_19_United_States_Australia_pre.json` | 0 |

At the same time, independent My Portfolio files do exist:

```text
data/history/my_portfolios/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json
data/history/my_portfolios/2026_06_19_United_States_Australia.json
```

Those files contain non-empty `items`, but the validation script does not load them.

## 4. 缺失环节

Missing link:

```text
Post-match validation does not join pre/post match snapshots with data/history/my_portfolios/*.json.
```

Current data flow:

```text
Post-match file
↓
Pre-match snapshot
↓
pre_snapshot["my_portfolio"]
↓
if embedded items exist, settle My Portfolio
↓
Validation Report
```

Actual saved My Portfolio flow:

```text
赛前录入
↓
data/history/my_portfolios/<match>.json
```

But this saved file path is currently not connected to:

```text
scripts/generate_post_match_validation_report.py
```

## 5. Current Actual Data Flow

Current implemented flow:

```text
data/history/*_post.json
↓
pre_match_snapshot field or inferred pre path
↓
load pre-match snapshot
↓
read strategy_snapshot.strategies
↓
attach shadow metadata
↓
settle Legacy Top / Scenario Top / Current Recommendation
↓
read pre_snapshot["my_portfolio"]["items"]
↓
if non-empty, settle My Portfolio
↓
POST_MATCH_VALIDATION_REPORT.md
```

Current gap:

```text
data/history/my_portfolios/*.json is outside this flow.
```

## 6. Desired Complete Data Flow

The intended complete flow should be:

```text
赛前录入 My Portfolio
↓
保存到 data/history/my_portfolios/<match_slug>.json
↓
赛后读取 post-match result / final_score
↓
找到对应 pre-match snapshot
↓
读取 strategy_snapshot.strategies
↓
读取 data/history/my_portfolios/<match_slug>.json
↓
结算 My Portfolio
↓
生成 My Portfolio Hit Status / P&L / ROI
↓
写入 POST_MATCH_VALIDATION_REPORT.md
```

## 7. Validation Result For Current System

Current answer:

```text
No, My Portfolio is not fully connected to the post-match validation system.
```

More precise statement:

```text
The script supports My Portfolio settlement only when My Portfolio is embedded in the pre-match snapshot. It does not read the canonical saved My Portfolio files under data/history/my_portfolios/.
```

## 8. Recommended Fix Scope

No code was changed during this check.

Recommended future implementation:

- Add a read-only loader for `data/history/my_portfolios/<match_slug>.json`.
- Match it by post/pre snapshot slug or match identity.
- Prefer the standalone My Portfolio file when it has non-empty `items`.
- Fall back to `pre_snapshot["my_portfolio"]` only when no standalone file exists.
- Add My Portfolio rows to `POST_MATCH_VALIDATION_REPORT.md` with:
  - Hit Status
  - P/L
  - ROI
  - Max Drawdown
  - Validation Result or portfolio outcome summary

Boundary:

- Do not modify historical data files.
- Do not change ranking.
- Do not change recommendation logic.
- Keep this as read-only validation/reporting.
