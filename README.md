# 世界杯分析器 MVP V1

这是一个给非技术用户使用的本地测试版。

当前版本可以：

- 输入一场比赛名称，例如：德国 vs 库拉索
- 使用模拟国际赔率
- 查询真实 Polymarket 市场价格
- 使用模拟新闻和伤病信息
- 生成结构化中文分析报告

当前版本还不能：

- 获取真实国际赔率
- 获取真实新闻和伤病
- 给出真实投注建议

## 本机运行步骤

### 1. 进入项目文件夹

```bash
cd worldcup-analyzer
```

### 2. 创建独立运行环境

```bash
python3 -m venv .venv
```

### 3. 启动独立运行环境

```bash
source .venv/bin/activate
```

### 4. 安装需要的软件包

```bash
pip3 install -r requirements.txt
```

### 5. 启动网页

```bash
streamlit run app.py
```

启动后，浏览器会打开本地网页。

如果没有自动打开，请访问：

```text
http://localhost:8501
```
