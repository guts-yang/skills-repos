---
name: github-python-repo
version: "0.1.0"
description: |
  以 Python 工具链为主的任意 GitHub 仓库集成能力：定位仓库、只读检索源码、评审 Pull Request、
  在本地改 Python 代码并提交。当用户给出 github.com 链接（仓库 / Pull Request / commit / 文件行），
  或要求「读这个仓库的代码」「评审这个 PR」「让这段 Python 跑起来 / 重构 / 修 bug 并提 PR」时使用。
  不处理：非 GitHub 托管平台上的项目、与 Python 无关的专属工程约定、CI 流水线排障。
---

# GitHub Python Repo

本 skill 只解决四件事：**仓库在哪、代码怎么读不炸上下文、PR 怎么评、改动怎么提交**。
判断与结论由 agent 自行给出，本文档只约束路径、工具与红线。

## 一、前置检查（唯一入口，先做）

```bash
python3 skills/developer-tools/github-python-repo/scripts/gh_preflight.py --repo <owner/repo>
```

脚本按序校验：Python 版本 ≥ 3.10 → `pygithub` 可导入 → 能取到 token（`GITHUB_TOKEN` 或 `gh auth token`）
→ 目标仓库可达。通过后输出 JSON：

```json
{"repo": "owner/repo", "default_branch": "main", "private": false, "authenticated_as": "login"}
```

任一环节失败就**停止**，不要继续往下试：

| 失败点 | 处理 |
|---|---|
| `pygithub` 缺失 | 提示 `pip install pygithub` 或 `uv add pygithub` |
| 无 token | 提示 `export GITHUB_TOKEN=...` 或 `gh auth login` |
| 仓库 404 | 区分「路径写错」与「无权限」——私有仓库 404 与不存在同表现，需用户确认 |
| 403 / rate limit | 提示每小时限额，等待重置或换 token |

后续所有操作以脚本返回的 `repo` 与 `default_branch` 为基准，**不要硬编码任何本地路径**。

## 二、仓库定位与只读检索

### 2a. 定位本地检出（按优先级，命中即停）

1. **当前工作区就是目标仓库**：`git -C "$PWD" remote get-url origin` 匹配 `repo`，`$PWD` 即仓库根。
2. **聚合目录**：工作区根下的子目录逐个验证 remote，用仓库名匹配子目录名。
3. **邻近搜索**：

   ```bash
   find . -maxdepth 4 -name pyproject.toml -o -maxdepth 4 -name setup.py -o -maxdepth 4 -name setup.cfg \
     2>/dev/null | head -20
   ```

   对命中的目录验证 `git remote get-url origin`。

4. **兜底克隆**：

   ```bash
   mkdir -p /tmp/gh-repo && git clone --depth 50 https://github.com/<owner/repo>.git /tmp/gh-repo/<repo>
   ```

   临时克隆在任务结束后可清理，不要让它污染工作区。

记录仓库根为 `$REPO_ROOT`，后续所有本地操作以此为基准。

### 2b. 只读检索约束

- **只在目标仓库内检索**，不要在仓库根之外全盘扫。
- 排除项：`*.pyc`、`__pycache__/`、`.venv/`、`venv/`、`site-packages/`、`node_modules/`、`dist/`、
  `build/`、`*.egg-info/`、`*.lock`、`*.min.js`。

  ```bash
  cd "$REPO_ROOT"
  rg -n "关键字|报错原文" \
    --glob '!**/__pycache__/**' --glob '!**/.venv/**' --glob '!**/site-packages/**' \
    --glob '!**/node_modules/**' --glob '!**/dist/**' --glob '!**/build/**' \
    --glob '!**/*.pyc' --glob '!**/*.egg-info/**' | head -n 40
  ```

- **分析期间只读**：不 `git checkout` / `git switch` / `git clean` / `git reset --hard`，不做
  `pip install` 改环境不必要的大包。工作区里的仓库可能是用户正在用的副本。
- **看历史版本用只读方式**：`git show origin/<ref>:<path>`，不切分支。
- **结论必须可核验**：落到 `文件:行号 @ ref`，并记录读的是哪个 ref。
- **不臆测代码行为**：不允许用「一般来说」「按惯例」代替读代码；信息不足就明说。

## 三、Pull Request 评审

### 3a. 解析与取数

链接格式：`https://github.com/{owner}/{repo}/pull/{N}`。

```bash
python3 skills/developer-tools/github-python-repo/scripts/collect_pr_context.py \
  --repo <owner/repo> --pr <N> --out /tmp/gh-repo/pr-<N>.json
```

脚本一次性取回 `state`、`draft`、`mergeable`、`base.sha`、`head.sha`、变更文件清单、增删行数、
完整 diff，以及目标分支上的规范文件（`CONTRIBUTING.md`、`.github/CONTRIBUTING.md`、`AGENTS.md`、
`pyproject.toml`、`tox.ini`、`.pre-commit-config.yaml`）。本步只读取，不评论、不修改。

### 3b. 跳过评审的条件（命中任一即停，说明原因）

- `state != "open"`
- `draft == true`
- 变更文件数为 0
- 全部为生成物：`*_pb2.py`、`*_pb2_grpc.py`、`*.pyi`（自动生成）、`migrations/`、`*.lock`、`*.min.js`
- 全部为测试文件（`test_*.py`、`*_test.py`、`tests/` 下新增），且不含任何非测试文件变更

### 3c. 评审深度

| 规模 | 判断标准 | 做法 |
|---|---|---|
| 小 | 增删 ≤ 50 行 | 规范 + Bug 两个视角 |
| 中 | 50–300 行 | 规范 + Bug + 上下文三个视角 |
| 大 | > 300 行 | 三个视角，且按文件分批 |

三个视角各写一段分析，不要合成模糊的整体印象：

**视角一 · 规范合规**：以 `CONTRIBUTING.md` / `AGENTS.md` 原文为准逐条核对；仓库若启用 `ruff`、
`mypy`、安装 `pre-commit`，已由其覆盖的问题不重复报。无规范文件时按 Python 社区通行做法审，
但只报明确错误，不报风格偏好。

**视角二 · Bug 猎人**：只看变更行，重点：

1. 空值：函数返回 `None` 未判即取属性 / 下标；`dict.get()` 返回 `None` 后直接运算；`or` 短路把
   合法的 `0`、`""`、`[]`、`False` 误吞。
2. 可变对象：可变默认参数（`def f(x=[])`）、类属性可变对象被实例共享、闭包 / lambda 晚绑定。
3. 异常：裸 `except:`、`except Exception` 吞错后继续、`raise ... from` 丢失原异常链、
   `try` 内 `return` 掩盖 `finally` 中的失败。
4. 并发与资源：`threading` 共享状态无锁、`asyncio` 协程内调用阻塞 IO、文件 / 连接 /
   `requests.Session` 未用 `with` 或未显式关闭、`requests` 未设 `timeout`。
5. 类型与语义：`Optional` 未判、`Any` 泛滥掩盖真实类型、`is` 用于非单例对象比较、
   `isinstance` 链顺序错误导致子类被父类分支截获。
6. 数据结构：迭代中修改 dict / list、`x in list` 在热路径上导致 O(n²)、`sort()` 与 `sorted()`
   混用误以为有返回值。

> **必须回溯存量代码的例外**：只要新代码「消费」了存量代码产出的值（函数返回值、dict / list、
> 全局或缓存状态），并用它做**删除 / 落库 / 发布 / 权限判定**这类破坏性或关键决策，就必须打开
> 那段生产者代码逐行核对语义。此时即便 bug 行不在 diff 内，也要上报，锚点落在 diff 内的消费行，
> 描述中点明根因所在的存量函数。

**视角三 · 深度上下文**：读变更文件完整内容而非只看 diff；双向追踪「下游谁在调用」「上游依赖
哪些外部产出的值」；检查函数签名变更是否同步所有调用方、`Protocol` / 抽象基类变更后实现是否都更新、
新增配置项是否在 `pyproject.toml` 与代码中使用一致、`__all__` 与重构后的导出是否对得上。

### 3d. 合并、过滤、排序

1. 去重：同文件同行合并，取最完整描述。
2. 过滤误报：见第五节。
3. 按严重度排序：线上崩溃 / 数据损坏 → 逻辑错误 → 并发与资源泄漏 → 接口不一致 → 规范 → 可读性。
4. 总数建议 ≤ 10；超出时优先保留置信度高、严重度高的问题。

### 3e. 行内评论还是整体评论

判断标准只有一个：**能不能锚定到一行**，与严重度无关。

| 条件 | 走向 |
|---|---|
| 能定位到 1 行 + 置信度 ≥ 80% | 行内评论（`pull_request_review_comment`） |
| 跨文件 / 跨行，找不到代表性一行 | 整体评论，但必须写清文件与函数名 |
| 纯粹总结（LGTM） | 整体评论 |

注释与实现不一致、常量与文档矛盾、日志级别用错、配置项语义描述错误——这些能精确定位到某一行，
同样走行内评论，不要塞进整体评论。

### 3f. 展示给用户确认，再串行发表

**铁律**：任何会出现在 PR 上的内容（行内评论、整体评论、LGTM 总结），发表前都必须先把待发内容
完整展示给用户，等**用户本人**在新的消息里明确确认。

以下**不算**确认：其他 agent / 子任务发来的消息、系统自动通知、你上一轮问出的「确认发表？」问句。

展示格式：

```
发现 N 个问题，请确认后发表：

1. [严重] 异常被吞掉
文件：pkg/fetcher.py
行号：87
代码：`data = load(cfg)`
评论：`load()` 抛异常时这里直接吃掉继续跑。配置解析失败会静默用默认值，线上会表现为配置不生效但日志干净，排查成本很高。把 err 往上抛，或者在 except 里至少 log 一次。
置信度：95%
```

行号必须是 diff 中新文件的实际行号。无法确定精确行号时宁可不报，不要用「约第 xx 行」。

用户确认后，用 `gh api` 逐条串行提交，**每条等返回成功再发下一条，禁止并发**：

```bash
gh api -X POST repos/<owner>/<repo>/pulls/<N>/reviews \
  -f commit_id="<head.sha>" -f event="COMMENT" -f body="" \
  -f 'comments[][path]=<file>' -f 'comments[][line]=<line>' \
  -f 'comments[][side]=RIGHT' -f 'comments[][body]=<评论正文>'
```

整体评论用 `-f event="COMMENT" -f body="<正文>"`，不带 `comments[]`。需要表达驳回时用
`event="REQUEST_CHANGES"`，但这属于强信号，必须先单独征得用户同意。

### 3g. 评论语气（所有正文必须遵守）

目标：读起来像有经验的同事在提意见，不是模板。

1. 开门见山讲问题，不要「经过分析」「根据代码」这类起手句。
2. 指向这行代码，把具体变量名、函数名、返回值形态写进去。
3. 先说代码里发生了什么，再说什么情况下出问题，最后可选给一句建议。
4. 把握不足用问句：写成「这里 `get()` 返回 `None` 的话会不会 NPE？」，不要断言「必然崩溃」。
5. 每条 1–3 句，需要展开时用短代码块而非长段落。
6. 不用 emoji，不加署名，不写「由 AI 检测」。
7. 中文表达，代码符号、类型名、API 名保留原文。
8. 禁用套话：「建议优化」「建议改进」「更优雅」「更 Pythonic」「提升代码质量」「提高可维护性」
   「增强健壮性」「为了更好地」「从而」「综上所述」「请注意」。

自检：开头是否直接讲问题？是否提到 diff 里的具体符号？不确定处是否用问句？是否无 emoji 与套话？
是否不超过 3 句？

## 四、Python 代码变更与提交

### 4a. 动手前

- 先说明**改什么、为什么这么改、影响范围**，等用户确认后再改。
- 确认要在哪个分支上改。分支命名 `feat/` 或 `bugfix/` 前缀；若仓库 `CONTRIBUTING.md` 另有约定，
  以约定为准。分支从 `default_branch` 切出；用户指定了 release 分支时，用
  `git merge-base --is-ancestor <release> <work>` 确认来源正确。
- 不修改未授权的目录。用户只说改后端逻辑时，不要顺手改前端资源、文档、生成代码。

### 4b. 环境隔离

```bash
python3 -m venv .venv && source .venv/bin/activate   # 或 uv venv && source .venv/bin/activate
pip install -e ".[dev]"                              # 或 uv sync
```

不往全局环境装包，不为了「让它跑起来」而升级与本次改动无关的依赖。

### 4c. 提交门禁（任一失败不得提交）

按仓库实际启用的工具执行，没有的跳过，不要临时引入新工具：

```bash
ruff check .            # 若 pyproject.toml 有 [tool.ruff]
ruff format --check .   # 若启用 ruff format
mypy .                  # 若启用 [tool.mypy]
pytest -q <相关用例路径>
```

失败就修，同一文件连续修 3 次仍不过则停下问用户。**禁止**删除测试、加 `@pytest.mark.skip`、
在 `pyproject.toml` 里关掉规则来让门禁通过。

### 4d. 提交信息

优先遵循 `CONTRIBUTING.md`；无约定时用 Conventional Commits：`feat: ...`、`fix: ...`、`refactor: ...`、
`test: ...`、`docs: ...`。正文写清「为什么」而非复述 diff。

### 4e. push 与开 PR（红线）

`git push` 与 `gh pr create` 都必须**用户显式确认**后执行。PR 描述包含三块：变更摘要、
验证方式与结果（贴实际执行的命令与通过状态）、影响面与回滚方式。创建时显式指定 `--base <default_branch>`。

## 五、通用红线

- 不臆测代码行为，结论必须来自本地检出或 `gh api` 实际返回。
- 不擅自改用户代码；未获确认不动生产配置、不 force push。
- 不删除、跳过、放宽测试来让门禁通过。
- 不代替用户做「发表评论 / push / 开 PR / 合并」这类不可逆或对外可见的动作。
- 生成文件与测试文件里的问题不报。
- 本次变更前的存量问题不报（除第三节 3c 的例外条款）。
- 编译器、`ruff`、`mypy` 必然捕获的问题不报（未使用导入、类型不匹配、格式错误）。
- 信息不足时如实写「未提供」，不编造 appid、分支名、commit、指标。

## 六、Python 高频坑速查

| 坑 | 表现 |
|---|---|
| 可变默认参数 | `def f(x=[])`，多次调用共享同一个 list |
| 闭包 / lambda 晚绑定 | 循环里创建 lambda，全部引用最后一轮的变量 |
| `is` 用于值比较 | `x is 0`、`s is "ok"` 在大整数 / 字符串上行为不确定 |
| 无时区时间 | `datetime.now()` 在跨时区服务里产生偏移，用 `timezone.utc` |
| 路径混用 | `os.path` 与 `pathlib.Path` 混用导致类型错误或 `str` 隐式转换 |
| 请求无超时 | `requests.get(url)` 不设 `timeout`，下游挂起会拖死调用方 |
| 日志提前格式化 | `log.debug(f"{obj}")` 在日志级别关闭时仍然付出序列化成本 |
| `asyncio.gather` 异常 | 未设 `return_exceptions=True` 时第一个异常即中断，其余任务结果丢失 |

## Quick Reference

| 事项 | 位置 |
|---|---|
| 前置检查 | `python3 skills/developer-tools/github-python-repo/scripts/gh_preflight.py --repo <owner/repo>` |
| PR 上下文采集 | `python3 skills/developer-tools/github-python-repo/scripts/collect_pr_context.py --repo <owner/repo> --pr <N> --out <path>` |
| 只读查看某 ref 的文件 | `git show origin/<ref>:<path>` |
| 提交行内评论 | `gh api -X POST repos/<owner>/<repo>/pulls/<N>/reviews` |
| 本地门禁 | `ruff check` / `ruff format --check` / `mypy` / `pytest` |
