#!/usr/bin/env python3
"""采集 Pull Request 的完整上下文，落成本地 JSON 供评审流程使用。

取回内容：PR 元信息、变更文件清单、完整 diff、目标分支上的项目规范文件。
本脚本只读取，不做任何写操作。

用法:
    python3 collect_pr_context.py --repo owner/repo --pr 42 --out /tmp/pr-42.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SPEC_FILES = (
    "CONTRIBUTING.md",
    ".github/CONTRIBUTING.md",
    "AGENTS.md",
    "CLAUDE.md",
    "pyproject.toml",
    "tox.ini",
    "setup.cfg",
    ".pre-commit-config.yaml",
    ".ruff.toml",
)

# 单文件 diff 的保留上限，避免超大生成物撑爆上下文
MAX_DIFF_CHARS = 200_000


def resolve_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    if shutil.which("gh") is None:
        raise SystemExit("未找到 GITHUB_TOKEN，且系统未安装 gh CLI")
    proc = subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, timeout=15, check=False
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise SystemExit("gh CLI 未登录，请执行 gh auth login 或设置 GITHUB_TOKEN")
    return proc.stdout.strip()


def fetch_pull(token: str, full_name: str, number: int):
    from github import Auth, Github

    client = Github(auth=Auth.Token(token), timeout=30, retry=2)
    repo = client.get_repo(full_name)
    return repo, repo.get_pull(number)


def fetch_spec_files(repo, ref: str) -> dict[str, str]:
    """读取目标分支上的规范文件，读不到就跳过，不重试。"""
    found: dict[str, str] = {}
    for path in SPEC_FILES:
        try:
            content = repo.get_contents(path, ref=ref)
        except Exception:
            continue
        if isinstance(content, list):
            continue
        try:
            found[path] = content.decoded_content.decode("utf-8", errors="replace")
        except Exception:
            continue
    return found


def build_payload(repo, pull) -> dict:
    files = []
    total_additions = 0
    total_deletions = 0
    for item in pull.get_files():
        patch = item.patch or ""
        truncated = len(patch) > MAX_DIFF_CHARS
        if truncated:
            patch = patch[:MAX_DIFF_CHARS] + "\n... [diff 已截断]"
        files.append(
            {
                "filename": item.filename,
                "status": item.status,
                "additions": item.additions,
                "deletions": item.deletions,
                "changes": item.changes,
                "previous_filename": item.previous_filename,
                "patch": patch,
                "truncated": truncated,
            }
        )
        total_additions += item.additions
        total_deletions += item.deletions

    spec_files = fetch_spec_files(repo, pull.base.ref)

    return {
        "repo": repo.full_name,
        "number": pull.number,
        "title": pull.title,
        "state": pull.state,
        "draft": pull.draft,
        "mergeable": pull.mergeable,
        "author": pull.user.login,
        "base": {"ref": pull.base.ref, "sha": pull.base.sha},
        "head": {"ref": pull.head.ref, "sha": pull.head.sha},
        "additions": total_additions,
        "deletions": total_deletions,
        "changed_files": len(files),
        "files": files,
        "spec_files": spec_files,
        "existing_review_notes": [
            {"user": note.user.login, "path": note.path, "line": note.line}
            for note in pull.get_review_comments()
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="采集 Pull Request 上下文")
    parser.add_argument("--repo", required=True, help="目标仓库，格式 owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Pull Request 编号")
    parser.add_argument("--out", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    token = resolve_token()
    repo, pull = fetch_pull(token, args.repo, args.pr)
    payload = build_payload(repo, pull)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "out": str(out_path),
                "state": payload["state"],
                "draft": payload["draft"],
                "changed_files": payload["changed_files"],
                "additions": payload["additions"],
                "deletions": payload["deletions"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
