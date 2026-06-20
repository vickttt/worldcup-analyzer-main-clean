# AI Collaboration Rules

## Roles

- ChatGPT 负责产品架构、任务拆分、路线判断。
- Codex 负责开发、测试、自动化执行。
- GitHub 负责版本记录。
- GitHub Desktop 负责提交、同步、回滚。

## Required Reading

- 所有 AI 开始工作前必须先阅读 `docs/`。
- 优先阅读 `docs/GPT_CONTEXT.md`、`docs/PRODUCT_PRINCIPLES.md`、`docs/TASK_QUEUE.md`、`docs/KNOWN_BUGS.md`、`docs/QA_REPORT.md`、`docs/CHANGELOG.md`。

## Branch And Version Safety

- 不允许在 `main` 分支直接做大改。
- 大功能必须新建 feature branch。
- 不允许 force push。
- 不允许重写 Git 历史。
- 不允许删除文件，除非用户明确批准。

## Required Documentation Updates

- 每次修改必须更新 `docs/CHANGELOG.md`。
- 每次开发后必须生成或更新 `docs/QA_REPORT.md`。
- 推荐逻辑相关修改必须检查剧本一致性。

## Product Safety Rules

- 推荐结果必须服务于清晰剧本。
- 不允许明显路径冲突的资产同时作为主推荐。
- Portfolio Ranking 是核心模块，相关修改必须保留可审计解释。

