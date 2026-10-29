# github-python-repo

以 Python 工具链为主的任意 GitHub 仓库集成 skill。给定一个 `github.com` 链接（仓库 / Pull Request / commit / 文件行），可以完成四件事：**定位仓库、只读检索源码、评审 Pull Request、提交 Python 代码变更**。

## 能力范围

- **仓库定位与只读检索**：按「当前工作区 → 聚合目录 → 邻近 `pyproject.toml` / `setup.py` → 临时克隆」的优先级找到目标仓库；检索时排除 `__pycache__`、`.venv`、`site-packages`、`dist`、`build` 等目录，避免上下文被噪声占满；所有结论强制落到 `文件:行号 @ ref`，不臆测代码行为
- **Pull Request 评审**：一次取回 PR 元信息、完整 diff 与目标分支上的项目规范文件（`CONTRIBUTING.md`、`pyproject.toml`、`tox.ini`、`.pre-commit-config.yaml` 等）；按 50 行 / 300 行两档分级，从规范合规、Bug 猎人、深度上下文三个视角分别审；合并去重后再按严重度排序，条数设上限
- **评论输出**：能锚定到行的走行内评论，跨文件的走整体评论；发表前必须由用户本人确认，确认后逐条串行提交，避免并发写入
- **Python 代码变更**：在隔离虚拟环境中修改，过 `ruff` / `mypy` / `pytest` 门禁后才提交；commit 遵循仓库约定，push 与开 PR 需显式确认

不处理：非 GitHub 托管平台上的项目、与 Python 无关的专属工程约定、CI 流水线排障。

## 目录结构

```
skills/developer-tools/github-python-repo/
├── SKILL.md                      # 技能主文档
├── README.md
└── scripts/
    ├── gh_preflight.py           # 前置检查：Python / PyGithub / token / 仓库可达
    └── collect_pr_context.py     # PR 上下文采集：元信息 + diff + 规范文件
```

## 依赖

- Python >= 3.10
- `pygithub`
- 可选 `gh` CLI（用于回退取 token、提交 PR 评论）

```bash
pip install pygithub
export GITHUB_TOKEN=<your_token>
```

## 快速验证

前置检查，确认解释器、PyGithub、token 与目标仓库均可用：

```bash
python3 skills/developer-tools/github-python-repo/scripts/gh_preflight.py --repo octocat/Hello-World
```

通过后输出：

```json
{
  "repo": "octocat/Hello-World",
  "default_branch": "master",
  "private": false,
  "authenticated_as": "<your_login>"
}
```

采集 PR 上下文：

```bash
python3 skills/developer-tools/github-python-repo/scripts/collect_pr_context.py --repo owner/repo --pr 42 --out /tmp/pr-42.json
```

## 触发场景

- 给出仓库、PR、commit 或文件行链接，要求读代码、定位某段逻辑
- 要求评审某个 Pull Request，或指出 diff 中的潜在缺陷
- 要求修改、重构、修复 Python 代码并提交，或准备 PR 描述

## 红线

- 发表评论、push、开 PR、合并之前，必须由用户本人确认
- 不删除、不跳过、不放宽测试来让门禁通过
- 不臆测代码行为，结论必须来自实际读到的代码或 API 返回
