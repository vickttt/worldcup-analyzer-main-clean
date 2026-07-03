#!/bin/zsh

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="${SCRIPT_DIR:h}"
PORT="8501"
URL="http://localhost:${PORT}/"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/streamlit_${PORT}.log"

open_app_url() {
  /usr/bin/open "$URL" >/dev/null 2>&1 || /usr/bin/open -a "Safari" "$URL" >/dev/null 2>&1 || {
    echo "浏览器没有自动打开，请手动访问：$URL"
  }
}

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || {
  echo "无法进入项目目录：$PROJECT_DIR"
  read "?按回车关闭窗口。"
  exit 1
}

echo "WorldCup Analyzer 启动器"
echo "项目目录：$PROJECT_DIR"
echo "网页地址：$URL"
echo ""

if [ ! -f "app.py" ]; then
  echo "启动失败：找不到 app.py。"
  read "?按回车关闭窗口。"
  exit 1
fi

if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
else
  PYTHON_BIN="$(command -v python3)"
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "启动失败：找不到可用 Python。"
  read "?按回车关闭窗口。"
  exit 1
fi

if ! "$PYTHON_BIN" -m streamlit --version >/dev/null 2>&1; then
  echo "启动失败：当前 Python 环境没有 Streamlit。"
  echo "可执行：$PYTHON_BIN -m pip install -r requirements.txt"
  read "?按回车关闭窗口。"
  exit 1
fi

if curl -fsS "$URL" >/dev/null 2>&1; then
  echo "网页已经在运行，正在打开浏览器。"
  open_app_url
  exit 0
fi

PORT_PIDS=$(lsof -ti tcp:${PORT} 2>/dev/null)
if [ -n "$PORT_PIDS" ]; then
  echo "发现 ${PORT} 端口有旧进程但网页不可访问，正在清理。"
  for pid in ${(f)PORT_PIDS}; do
    kill "$pid" 2>/dev/null
  done
  sleep 2
fi

echo "正在启动 Streamlit..."
echo "日志文件：$LOG_FILE"
echo ""

(
  cd "$PROJECT_DIR" || exit 1
  exec "$PYTHON_BIN" -m streamlit run app.py \
    --server.port "$PORT" \
    --server.headless true \
    --browser.gatherUsageStats false
) > "$LOG_FILE" 2>&1 &
STREAMLIT_PID=$!
disown "$STREAMLIT_PID" 2>/dev/null || true
echo "$STREAMLIT_PID" > "$LOG_DIR/streamlit_${PORT}.pid"

for i in {1..90}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    echo "网页已启动：$URL"
    open_app_url
    echo "可以关闭这个 Terminal 窗口，网页服务会继续在后台运行。"
    exit 0
  fi
  sleep 1
done

echo "90秒内没有检测到网页响应，请查看日志：$LOG_FILE"
read "?按回车关闭窗口。"
exit 1
