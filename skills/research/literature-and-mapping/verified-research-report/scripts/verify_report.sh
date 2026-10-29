#!/usr/bin/env bash
# 研究报告机械核验脚本 · verified-research-report skill
#
# 用法:
#   bash verify_report.sh <报告文件.md> [更多.md ...]
#
# 逐项检查：
#   1. LaTeX $ 分隔符配平（总数偶数 + 无奇数行 + $$ 块成对）
#   2. 参考文献编号连续 1..N（无跳号、无重复）
#   3. 正文引用集合 <-> 参考文献集合 双向差集（悬空引用 / 孤儿条目）
#   4. 禁用名称扫描（应仅出现在勘误告知句中）
#   5. 形似占位符的 ID / 非论文出处链接扫描
#
# 退出码：全部通过 0；任一失败 1

set -uo pipefail
fail=0

if [ $# -eq 0 ]; then
  echo "用法: bash verify_report.sh <报告文件.md> [...]" >&2
  exit 2
fi

for F in "$@"; do
  if [ ! -f "$F" ]; then echo "跳过（不存在）: $F"; continue; fi
  echo "=============================================="
  echo "文件: $F"
  echo "=============================================="

  # ---- 1. $ 配平 ----
  tot=$(grep -o '\$' "$F" | wc -l | tr -d ' ')
  odd=$(awk '{n=gsub(/\$/,"$"); if(n%2==1) c++} END{print c+0}' "$F")
  dd=$(grep -o '\$\$' "$F" | wc -l | tr -d ' ')
  parity=$([ $((tot % 2)) -eq 0 ] && echo OK || echo FAIL)
  ddp=$([ $((dd % 2)) -eq 0 ] && echo OK || echo FAIL)
  echo "[1] LaTeX 配平: \$总数=$tot ($parity)  奇数行=$odd ($([ "$odd" -eq 0 ] && echo OK || echo FAIL))  \$\$块=$((dd/2)) ($ddp)"
  { [ "$parity" = OK ] && [ "$odd" -eq 0 ] && [ "$ddp" = OK ]; } || fail=1

  # ---- 2. 参考文献编号连续性 ----
  ids=$(grep -oE '^\[[0-9]+\]' "$F" | grep -oE '[0-9]+' | sort -n)
  n=$(echo "$ids" | grep -c . || true)
  if [ "$n" -gt 0 ]; then
    seq_ok=$([ "$(echo "$ids" | tr '\n' ' ')" = "$(seq 1 "$n" | tr '\n' ' ')" ] && echo OK || echo FAIL)
    max=$(echo "$ids" | tail -1)
    echo "[2] 参考文献: $n 条, 最大编号=$max, 连续1..$n=$seq_ok"
    [ "$seq_ok" = OK ] || fail=1
  else
    echo "[2] 参考文献: 未找到 '^[n] ' 形式条目（若该文件不是报告正文可忽略）"
  fi

  # ---- 3. 引用集合双向差集 ----
  tmp=$(mktemp -d)
  grep -oE '\[[0-9]+\]' "$F" | tr -d '[]' | sort -n -u > "$tmp/intext.txt"
  grep -oE '^\[[0-9]+\]' "$F" | tr -d '[]' | sort -n -u > "$tmp/reflist.txt"
  dangling=$(comm -23 "$tmp/intext.txt" "$tmp/reflist.txt" | tr '\n' ' ')
  orphan=$(comm -13 "$tmp/intext.txt" "$tmp/reflist.txt" | tr '\n' ' ')
  echo "[3] 悬空引用(正文有/文献无): ${dangling:-无}"
  echo "    孤儿条目(文献有/正文未引): ${orphan:-无}"
  [ -z "${dangling// /}" ] && [ -z "${orphan// /}" ] || fail=1
  rm -rf "$tmp"

  # ---- 4. 禁用名称 ----
  hit=$(grep -nE 'MMUnlearnBench|SIUO|MLLM-Unlearning' "$F" | wc -l | tr -d ' ')
  echo "[4] 禁用名称命中行数: $hit （须仅出现在勘误告知句中；请人工确认下方输出）"
  grep -nE 'MMUnlearnBench|SIUO|MLLM-Unlearning' "$F" | cut -c1-160 | sed 's/^/      /'

  # ---- 5. 可疑链接 ----
  # 判据说明（启发式，非充分条件）：OpenReview 真实 forum ID 是短随机串
  # （如 M476xkfNXe / 9OJflnNu6C / 6WYjBeIioq，最长连续字母串通常 =<8），
  # 而语义化占位符（如 ControllableUnlearningI2I）含 >=10 个连续字母。
  # 阈值取 10，避免误报真实随机 ID。
  echo "[5] 可疑链接（启发式；占位符形 ID / 非论文出处）："
  grep -oE 'https?://[^ )，）]+' "$F" \
    | grep -Ei 'openreview\.net/forum\?id=[A-Za-z0-9]*[A-Za-z]{10,}|github\.com/[^/]+/[^/]+$|aiconfpaper|arxivlens|=placeholder|XXX' \
    | sort -u | sed 's/^/      /' || true
  echo "      （以上为空则通过；非空时须逐条打开核对标题是否匹配——启发式会有误报，以实际打开结果为准）"

  echo
done

echo "=============================================="
if [ "$fail" -eq 0 ]; then echo "结论: 全部机械核验通过 ✓"; else echo "结论: 存在失败项 ✗（见上）"; fi
exit $fail
