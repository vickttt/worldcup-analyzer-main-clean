# Product Review V1

Date: 2026-06-21

Scope: product review only. This review does not design new modules, write code, change business logic, modify UI, modify data files, create branches, commit, or push.

## 1. 当前系统最成功的 3 个地方

1. Portfolio Ranking 已经成为真正的决策核心。
   - 系统不再只给单一推荐，而是把多个组合放到同一个比较框架里。
   - Legacy Rank、Scenario Rank、Shadow Verdict 同屏后，用户能看到“当前正式排序”和“剧本视角排序”的差异。

2. 项目已经从“赔率指标堆叠”转向“剧本一致性”。
   - Scenario Engine、Recommendation Auditor、Shadow Mode 已经形成一条清晰链路。
   - 当前产品最强的方向是：先判断比赛剧本，再判断资产是否服务剧本。

3. 数据和审计资产积累得很好。
   - pre/post snapshot、history、audit report、shadow report 都在沉淀。
   - 这让项目未来可以回放、复盘、比较 Legacy Ranking 和 Scenario Ranking，而不是只凭主观感觉改模型。

## 2. 当前系统最失败的 3 个地方

1. 页面信息密度过高，用户必须自己筛选重点。
   - 核心决策、球队信息、市场盘口、赛后总结、数据来源都存在，但优先级没有被产品层强制压缩。
   - 用户打开页面后仍然容易陷入“看很多指标，但不知道该不该下注”的状态。

2. 核心推荐的解释还不够像“下注决策”。
   - 当前能解释 EV、ROI、最大亏损、剧本一致性，但用户最关心的是：为什么买、为什么不买、最大风险是什么。
   - 现有说明更像分析报告，不像交易决策卡片。

3. 低价值模块占用了过多页面注意力。
   - 数据来源、技术说明、市场调试、完整盘口表、球队资料等内容对开发和审计有用，但对普通决策用户不够直接。
   - 这些内容应该成为后台或折叠区，而不是默认参与主决策体验。

## 3. 当前页面哪些内容用户根本不会看

- 数据来源里的技术说明和调试信息。
- 完整 Data Completeness 明细。
- 大段市场缓存、接口、source 解释。
- 过长的球队资料介绍。
- 低优先级盘口明细表。
- Polymarket 与传统盘口并列的大量原始字段。
- Post-match 页面在赛前决策场景下不会被普通用户主动查看。
- 高阶研究区里的过多中间指标。

判断标准：

- 如果信息不能直接回答“买什么、为什么、风险是什么、是否和剧本一致”，普通用户大概率不会看。

## 4. 当前页面哪些内容最有决策价值

1. Portfolio Ranking 表格。
   - 这是当前最有价值的决策入口。
   - 特别是 Legacy Rank、Scenario Rank、Shadow Verdict、主剧本、EV、ROI、最大亏损。

2. 风险提示。
   - 用户最终需要知道哪些比分路径会让组合失败。
   - 风险提示比盘口明细更接近真实下注决策。

3. 主路径结构。
   - 方向、大小球、波胆路径能快速判断推荐是否服务同一个剧本。

4. 我的组合。
   - 如果用户已经有下注想法，系统能帮他判断自己的组合在同一套逻辑下排第几。

5. Scenario / Shadow 信号。
   - 当前还不应替代 Legacy 排名，但已经能暴露 Legacy Rank 1 与 Scenario Rank 不一致的问题。

## 5. 哪些模块应该保留

- Portfolio Ranking。
- Visible Shadow Mode MVP。
- Scenario Engine。
- Recommendation Auditor。
- My Portfolio。
- 风险提示。
- 主路径结构。
- pre/post snapshot 和历史数据库。
- 赛后总结，但应作为复盘模块，不应干扰赛前主决策。
- 数据来源页，但应作为调试/审计模块。

## 6. 哪些模块应该隐藏

- 数据来源。
- Data Completeness。
- 技术说明。
- 高阶研究。
- 市场调试摘要。
- 完整盘口原始表。
- 球队资料长文本。
- Post-match Analysis 在赛前场景下默认隐藏。
- Kelly 参考和边际贡献分析默认隐藏。

隐藏原则：

- 对开发、审计、复盘有用的内容不删除。
- 对普通用户决策没有直接帮助的内容默认折叠。

## 7. 哪些模块应该删除

不建议马上物理删除代码或数据。

产品层面应从主流程删除的内容：

- 重复表达同一结论的盘口明细。
- 只展示原始数据、不形成判断的表格。
- 与“下注决策”无关的长说明。
- 无法解释推荐变化的中间指标。

删除标准：

- 如果一个模块连续无法影响“买什么、避开什么、为什么”三个问题，就不应留在主页面。

## 8. 如果只能保留一个页面、一个表格、一个推荐

一个页面：

- 核心决策页。

一个表格：

- Portfolio Ranking 表格。

一个推荐：

- Legacy Rank 1 的组合仍作为正式推荐，但必须同时显示 Scenario Rank 和 Shadow Verdict。

理由：

- 当前还没有足够样本证明 Scenario Ranking 可以替代 Legacy Ranking。
- 但 Shadow Verdict 已经证明它能提供额外决策信息，所以不能隐藏。

## 9. 当前产品打分

| 维度 | 分数 | 评价 |
| --- | ---: | --- |
| 数据层 | 8 / 10 | 本地历史、pre/post、snapshot 基础较强，适合复盘和审计。 |
| 决策层 | 7 / 10 | Portfolio Ranking 已成核心，但 Ranking 仍未真正生产化使用 Scenario 信号。 |
| UI 层 | 5 / 10 | 功能完整，但信息优先级混乱，用户需要自己找重点。 |
| 用户体验 | 5 / 10 | 专业用户能用，普通决策用户负担偏重。 |
| 产品整体 | 6.5 / 10 | 方向正确，底层强于前台，当前最大问题是决策呈现不够克制。 |

## 10. 下一阶段唯一最值得开发的功能

唯一选择：

- Portfolio Ranking 决策表瘦身。

定义：

- 保持 Legacy 排名不变。
- 保持推荐逻辑不变。
- 保持 score 不变。
- 默认只展示真正影响下注决策的字段。
- 把低价值字段和技术信息移入折叠区。

原因：

- 当前系统不是缺更多模型，而是缺一个足够清晰的决策界面。
- Scenario Rank 和 Shadow Verdict 已经进入表格，下一步最值得做的是让 Portfolio Ranking 成为唯一主决策面。
- 如果继续增加模块，会进一步放大信息过载问题。

一句话结论：

- 当前产品最该做的不是更聪明，而是更少、更准、更像一个下注决策台。
