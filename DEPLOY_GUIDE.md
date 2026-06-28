# Streamlit Cloud 部署指南

本文档用于把 WorldCup Analyzer 部署到 Streamlit Cloud，获得公开访问网址。

## 1. 部署前检查

项目需要包含：

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `.streamlit/secrets.example.toml`
- `.gitignore`

不要提交：

- `.streamlit/secrets.toml`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `logs/`
- `outputs/reports/`
- 任何真实 API Key

当前项目不需要 `packages.txt`，因为没有系统级 Linux 依赖。

## 2. GitHub 创建仓库

1. 打开 GitHub。
2. 点击右上角 `+`。
3. 选择 `New repository`。
4. Repository name 可填写：

```text
worldcup-analyzer
```

5. 选择 `Private` 或 `Public`。
6. 不要勾选自动创建 README、`.gitignore` 或 License。
7. 点击 `Create repository`。

## 3. Git 推送命令

在本机终端进入项目目录：

```bash
cd /Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer
```

确认不会提交密钥：

```bash
git status
```

添加文件：

```bash
git add .
```

提交：

```bash
git commit -m "Prepare Streamlit Cloud deployment"
```

连接 GitHub 仓库。把下面 URL 换成你自己的 GitHub 仓库地址：

```bash
git remote add origin https://github.com/YOUR_USERNAME/worldcup-analyzer.git
```

如果已经存在 `origin`，改用：

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/worldcup-analyzer.git
```

推送：

```bash
git branch -M main
git push -u origin main
```

## 4. Streamlit Cloud 配置步骤

1. 打开 Streamlit Cloud。
2. 使用 GitHub 登录。
3. 点击 `Create app` 或 `New app`。
4. 选择你的 GitHub 仓库：

```text
worldcup-analyzer
```

5. Branch 选择：

```text
main
```

6. Main file path 填写：

```text
app.py
```

7. Python 版本建议选择：

```text
3.11 或 3.12
```

8. 点击 `Advanced settings`，填写 Secrets。

## 5. Streamlit Cloud Secrets

在 Streamlit Cloud 的 Secrets 输入框中填写：

```toml
API_FOOTBALL_KEY = "你的 API-Football Key"
API_FOOTBALL_KEY = "你的 API-Football Key"
```

不要把真实 Key 写进 GitHub。

## 6. 部署后检查

部署完成后，打开 Streamlit Cloud 给出的公开网址。

测试输入：

```text
Argentina vs Algeria
```

点击：

```text
生成赛前分析
```

应能看到：

- 2026 世界杯赛事 Banner
- 投注观点
- 决策引擎 V1
- 胜平负赔率
- 亚洲让球盘
- 大小球盘口
- Polymarket 预测市场
- 球队信息

## 7. 常见问题

### 缺少 API Key

如果页面提示缺少 API Key，请检查 Streamlit Cloud Secrets 是否填写：

```toml
API_FOOTBALL_KEY = "..."
API_FOOTBALL_KEY = "..."
```

### 部署失败，提示安装依赖失败

检查 `requirements.txt` 是否存在，并确认内容类似：

```text
streamlit==1.41.1
pyyaml==6.0.2
requests>=2.32.0,<3
```

### 页面能打开，但没有赔率

可能原因：

- API-Football Key 未配置
- API-Football 免费额度用完
- 当前比赛没有对应市场

### API-Football 免费版提示额度或 season 权限

这是免费版限制。当前系统对部分 fixture 和球队资料有本地兜底，不影响页面基本展示。
