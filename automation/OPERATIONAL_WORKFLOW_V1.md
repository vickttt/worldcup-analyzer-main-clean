# DEPRECATED — HISTORICAL REFERENCE ONLY

This document is no longer an active workflow authority.
The current active repository rules are defined only in AGENTS.md.

Current active workflow:
- dev-clean is the only development branch
- no automatic branch creation or branch switching
- Codex is the only execution engine
- Claude is read-only review only
- the user is the final decision authority
- no parallel agent workflows are allowed
- old Issue -> Branch -> PR, Supervisor-driven branch workflows, and multi-agent automation loops must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# Operational Workflow v1

Date: 2026-06-21

Scope: workflow design only. This document does not write code, change system behavior, modify UI, modify recommendation logic, modify data files, create branches, commit, or push.

## Goal

Define how the World Cup Analyzer should be used every day.

The operating principle is:

```text
Pre-match decisions stay disciplined.
Scenario Rank observes and warns.
Post-match validation proves whether Scenario Ranking deserves promotion.
```

## 1. 赛前流程

### Step 1: 数据刷新

Purpose:

- Ensure pre-match odds, fixture, market, and team context are current before analysis.

Owner:

- Human operator or terminal automation.

Rule:

- API data is refreshed through terminal scripts.
- The web page only displays data.
- Historical `pre` snapshots must be preserved.

Inputs:

- fixture data
- odds data
- market data
- Polymarket data when available
- existing historical snapshots

Output:

- updated local data files or refreshed local cache
- pre-match snapshot candidate

### Step 2: 生成分析

Purpose:

- Generate the match analysis before kickoff using current data.

Required outputs:

- match overview
- main path structure
- risk notes
- recommendation combo
- Portfolio Ranking

Quality check:

- The analysis must answer:
  - What is the main match script?
  - What portfolio is formally ranked first?
  - What can go wrong?

### Step 3: Portfolio Ranking

Purpose:

- Provide the official production ranking.

Current rule:

- Legacy Ranking remains the official order.
- Legacy `score` remains authoritative.
- Sorting must not be changed during operation.

Default table should focus on:

- Portfolio name
- Scenario Rank
- Shadow Verdict
- Main script
- EV
- ROI
- Max loss
- Scenario consistency score
- Overall score

### Step 4: Scenario Rank

Purpose:

- Observe whether scenario-aware ranking agrees with Legacy Ranking.

Current rule:

- Scenario Rank is not the official order.
- Scenario Rank is used as decision support and validation evidence.
- Scenario Rank should be checked whenever Legacy Rank 1 differs from Scenario Rank 1.

### Step 5: Shadow Verdict

Purpose:

- Quickly label whether Legacy Ranking and Scenario Ranking agree.

Interpretation:

| Verdict | Meaning | Operational Action |
| --- | --- | --- |
| Agreement | Legacy and Scenario broadly agree. | Normal review. |
| Watch | Some ranking movement exists. | Read risk notes before betting. |
| Disagreement | Scenario materially disagrees. | Do not blindly trust Legacy Rank 1. |
| Blocker Candidate | High-risk observation. | Treat as not default-safe until reviewed. |

## 2. 下注决策流程

### Step 1: 正式推荐

Current formal recommendation:

- Legacy Rank 1 remains the official recommendation.

Before acting, confirm:

- Legacy Rank 1 portfolio
- EV / ROI / max loss
- main script
- Shadow Verdict
- risk notes

### Step 2: Scenario 观察

If Scenario Rank 1 equals Legacy Rank 1:

- Proceed with normal confidence, subject to risk notes.

If Scenario Rank 1 differs from Legacy Rank 1:

- Compare:
  - Why Legacy Rank 1 is first
  - Why Scenario Rank 1 is first
  - Whether Legacy Rank 1 is tail-heavy, pure tempo, or low consistency
  - Whether Scenario Rank 1 better serves the match script

Current rule:

- Scenario Rank may warn.
- Scenario Rank may influence caution.
- Scenario Rank does not yet replace the official ranking.

### Step 3: 我的组合

Purpose:

- Let the user compare their intended bet against the same decision framework.

Manual action:

- Enter or review My Portfolio.

Check:

- Does My Portfolio serve the same main scenario?
- Is it more tail-heavy than the official recommendation?
- Does it rank worse than both Legacy Top and Scenario Top?
- Does it introduce path conflicts?

Decision rule:

- If My Portfolio performs worse and has worse Shadow Verdict, the user should either reduce stake or revise the portfolio.

## 3. 赛后流程

### Step 1: 结果写入

Purpose:

- Preserve the final match result for validation.

Required fields:

- final score
- winner result
- total goals
- handicap result
- total market result
- correct-score result

Rule:

- Final result must be linked to the original pre-match snapshot.
- Do not overwrite pre-match reasoning.

### Step 2: Post-Match Validation

Purpose:

- Compare Legacy Top vs Scenario Top using actual settlement outcomes.

Run:

```text
scripts/generate_post_match_validation_report.py
```

Output:

```text
POST_MATCH_VALIDATION_REPORT.md
```

Validation compares:

- Legacy Top Portfolio
- Scenario Top Portfolio
- Current Recommendation
- My Portfolio when available

Metrics:

- hit status
- P/L
- ROI
- max drawdown
- Legacy vs Scenario Winner

### Step 3: Decision Journal

Purpose:

- Preserve why the system believed something before the match and whether that belief was correct.

Each journal should record:

- pre-match formal recommendation
- main scenario
- Scenario warning
- Shadow Verdict
- Legacy Top reason
- Scenario Top reason
- final result
- validation conclusion

Rule:

- The journal should judge the decision process, not only the final score.

## 4. 每日检查流程

### WorldCup Supervisor

Daily checks:

- current branch
- uncommitted files
- whether work is happening on `main`
- whether `docs/CHANGELOG.md` was updated after changes
- whether `docs/QA_REPORT.md` was updated after development
- whether `docs/TASK_QUEUE.md` still matches current priorities

Daily output:

- project status
- current priority
- known issues
- recommended next step

### QA

Daily QA should confirm:

- no accidental data overwrite
- no unintended recommendation logic change
- no unintended ranking sort change
- reports were regenerated when required
- latest automation ran successfully

### Validation

Daily validation should confirm:

- post-match results were added when available
- `POST_MATCH_VALIDATION_REPORT.md` is current
- number of valid post-match validations
- whether 5-Match Promotion Rule is satisfied

Current promotion rule:

- With fewer than 5 valid post-match validations: keep Shadow Mode.
- After 5 valid validations: review whether Scenario Guardrails Phase should begin.

## 5. 哪些步骤自动

Should be automated:

- reading pre-match snapshots
- identifying Legacy Top Portfolio
- identifying Scenario Top Portfolio
- attaching Shadow Metadata
- generating Shadow Verdict
- generating post-match validation report
- calculating P/L and ROI from final score
- calculating Legacy vs Scenario Winner
- generating daily QA/report summaries

Can be automated later:

- batch validation across all post-match snapshots
- alert when Legacy Rank 1 has Shadow Verdict = Disagreement
- alert when 5-Match Promotion Rule becomes eligible

## 6. 哪些步骤人工

Should remain manual:

- deciding whether to place a bet
- deciding stake size
- interpreting match context that data cannot capture
- confirming final score and settlement source
- deciding whether Scenario Guardrails Phase should begin
- deciding whether to promote any Scenario signal into production ranking

Reason:

- The system is decision support, not an autonomous betting agent.
- Ranking evidence is still early and must be validated across completed matches.

## 7. 当前项目阶段

Current stage:

```text
Development
```

Reason:

- Core governance exists.
- Scenario Engine exists as design and report automation.
- Recommendation Auditor exists as design/report workflow.
- Shadow Metadata and Visible Shadow Mode MVP exist.
- Portfolio Ranking table has been slimmed into a better decision surface.
- Post-Match Validation Automation v0.1 exists.

But the project is not yet in full Operation because:

- Only 2 valid post-match validations exist.
- The 5-Match Promotion Rule has not been satisfied.
- Scenario Rank is still observational.
- Legacy Ranking is still official.
- Daily operating discipline is not yet fully automated.

Operational readiness target:

```text
Enter Operation after at least 5 valid post-match validations and a stable daily workflow.
```

## 8. Daily Operating Checklist

### Before Matches

- Refresh data through terminal script.
- Generate or open pre-match analysis.
- Review Portfolio Ranking.
- Check Scenario Rank and Shadow Verdict.
- Review risk notes.
- Compare My Portfolio if user has one.

### Before Betting

- Confirm Legacy Rank 1.
- Confirm Scenario Rank 1.
- Confirm Shadow Verdict.
- Confirm max loss.
- Confirm main scenario.
- Decide manually.

### After Matches

- Record final score.
- Run post-match validation report.
- Update Decision Journal.
- Check Legacy vs Scenario Winner.
- Update validation count toward 5-match rule.

### End Of Day

- Run Supervisor check.
- Confirm QA report status.
- Confirm no unintended code/data changes.
- Confirm next priority.

## 9. Operating Principle

The project should not chase more indicators.

The daily workflow should force one clear sequence:

```text
Data
→ Scenario
→ Ranking
→ Human decision
→ Post-match validation
→ Promotion evidence
```

Until evidence proves otherwise:

```text
Legacy Ranking decides.
Scenario Ranking observes.
Post-match validation judges both.
```
