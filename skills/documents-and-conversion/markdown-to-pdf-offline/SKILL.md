---
name: markdown-to-pdf-offline
description: 在没有 pandoc / wkhtmltopdf 且 Chrome headless 无法运行（沙箱崩溃）的 macOS 环境下，把 Markdown 或 CSV 转成排版良好的中文 PDF。触发词：输出 PDF、转 PDF、生成 PDF 版本、导出 PDF。使用 reportlab + 系统中文字体，支持表格自适应列宽、跨页表头重复、页码页脚。
description_zh: "Markdown/CSV 转 PDF（无 pandoc/Chrome 环境）"
description_en: "Convert Markdown/CSV to PDF without pandoc or Chrome"
disable: false
agent_created: true
---

# markdown-to-pdf-offline

## When to use
- 用户要求把 .md / .csv 文件"输出 PDF / 转 PDF / 导出 PDF 版本"
- 已探测环境缺少 pandoc / weasyprint / wkhtmltopdf，且 Chrome headless 崩溃或挂起（见 Pitfalls 第 1 条，先探测再走本方案）

## Steps
1. **环境探测**（一条命令）：
   ```bash
   which pandoc weasyprint wkhtmltopdf; ls -d "/Applications/Google Chrome.app" 2>/dev/null
   python -c "import markdown, reportlab" 2>&1
   ```
2. **若 Chrome 存在**，先用 35s 超时的最小用例测试 headless 是否可用（`--print-to-pdf` + 极简 HTML）。可用则优先 Chrome（CSS 支持最好）；不可用（挂起或 SIGSEGV）→ 走本 skill 脚本。
3. **安装依赖**（managed venv，不污染全局）：
   ```bash
   ~/.workbuddy/binaries/python/versions/3.13.12/bin/python3 -m venv ~/.workbuddy/binaries/python/envs/default   # 已存在则跳过
   ~/.workbuddy/binaries/python/envs/default/bin/pip install -q markdown reportlab
   ```
4. **运行脚本**（scripts/md2pdf.py，按扩展名自动路由 .md / .csv）：
   ```bash
   # Markdown（纵向 A4）
   ~/.workbuddy/binaries/python/envs/default/bin/python <skill>/scripts/md2pdf.py in.md out.pdf --title "标题" --subtitle "副题"
   # CSV 大表（横向 A4 + 手动列宽比例）
   ~/.workbuddy/binaries/python/envs/default/bin/python <skill>/scripts/md2pdf.py in.csv out.pdf --landscape --col-ratio "0.05,0.1,0.05,0.085,0.065,0.33,0.05,0.05,0.055,0.23"
   ```
5. **校验**（pypdf 查页数与文本；pymupdf 渲染 PNG 目检）：
   ```bash
   pip install -q pypdf pymupdf
   python -c "from pypdf import PdfReader; print(len(PdfReader('out.pdf').pages))"
   python -c "import pymupdf; pymupdf.open('out.pdf')[0].get_pixmap(dpi=110).save('/tmp/p1.png')"
   ```
   然后 Read 渲染出的 PNG 目检排版（宽表是否折行、中文是否乱码）。

## Pitfalls
- **Chrome headless 在沙箱环境不可用**：`--headless` 挂起至超时；`--single-process` 直接 SIGSEGV（`CVDisplayLinkCreateWithCGDisplay failed` / `Mach rendezvous failed`）。不要反复重试 Chrome，直接切 reportlab 路线。
- **reportlab 不支持 postscript outlines 的 TTC**：`/System/Library/Fonts/Hiragino Sans GB.ttc`、`STHeiti*.ttc`、`PingFang.ttc` 全部会报 "postscript outlines are not supported"。**macOS 上唯一稳定的单文件中文字体是 `/Library/Fonts/Arial Unicode.ttf`**，脚本已按此顺序探测。
- **emoji 黑块**：Arial Unicode 无 ⚠️✅❌ 等字形，渲染成豆腐块。脚本 `clean()` 已替换为 `[!]` `[OK]` `[X]`。新字体/新符号同样先替换再渲染。
- **宽表等宽列宽会把短列挤到竖排折行**（如 `W10` 变 `W1/0`）：脚本对 md 表格按"各列内容最大视觉长度（中文算 2）"自适应分配列宽，并设 `MINW = min(26pt, 5% 宽)` 下限。若仍折行，增大 MINW。
- **reportlab 传参坑**：`colWidths` 传 list 时不能再写 `[cw] * ncol`（会产生嵌套 list，报 `unsupported operand type(s) for -=: 'float' and 'list'`）。
- **CSV 跨页表头**：必须 `repeatRows=1`，否则第 2 页起没有列名。
- 大 markdown（含几十张表）转换约需数秒，属正常；用 Bash 默认超时即可，无需 run_in_background。

## Verification
- `pypdf`：页数合理、`extract_text()` 无 `�`/`□`、关键小节标题在文本中可检索到。
- `pymupdf` 渲染首页 + 含最宽表格的页 → Read PNG 目检：列宽无异常折行、表头蓝底白字、斑马纹正常、页脚页码存在。
