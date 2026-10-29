#!/usr/bin/env python3
"""GitHub 仓库前置检查。

按序校验 Python 版本、PyGithub 可用性、token 获取、目标仓库可达，
通过后输出 JSON 供后续流程使用。任一环节失败即刻退出并给出可执行的处理建议。

用法:
    python3 gh_preflight.py --repo owner/repo
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

MIN_PYTHON = (3, 10)


class PreflightError(Exception):
    """前置检查失败，携带面向用户的可执行建议。"""

    def __init__(self, stage: str, message: str, hint: str) -> None:
        super().__init__(message)
        self.stage = stage
        self.message = message
        self.hint = hint


def check_python() -> str:
    if sys.version_info < MIN_PYTHON:
        raise PreflightError(
            "python",
            f"Python 版本过低: {sys.version.split()[0]}",
            "升级到 3.10 及以上，或改用 pyenv / uv 选择解释器",
        )
    return sys.version.split()[0]


def check_pygithub():
    try:
        from github import Github  # noqa: F401
    except ImportError as exc:
        raise PreflightError(
            "pygithub",
            f"pygithub 不可导入: {exc}",
            "pip install pygithub 或 uv add pygithub",
        ) from exc
    try:
        import github as github_pkg

        return getattr(github_pkg, "__version__", "unknown")
    except Exception:  # pragma: no cover - 版本属性缺失不影响主流程
        return "unknown"


def resolve_token() -> tuple[str, str]:
    """返回 (token, 来源)。先读环境变量，再回退到 gh CLI。"""
    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token:
        return env_token.strip(), "env"

    if shutil.which("gh") is None:
        raise PreflightError(
            "token",
            "未找到 GITHUB_TOKEN 且系统未安装 gh CLI",
            "export GITHUB_TOKEN=<你的 token>，或安装 gh 后执行 gh auth login",
        )

    try:
        proc = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except subprocess.SubprocessError as exc:
        raise PreflightError(
            "token", f"调用 gh auth token 失败: {exc}", "执行 gh auth login 重新登录"
        ) from exc

    token = proc.stdout.strip()
    if proc.returncode != 0 or not token:
        raise PreflightError(
            "token",
            "gh CLI 未登录或无可用 token",
            "执行 gh auth login，或 export GITHUB_TOKEN=<你的 token>",
        )
    return token, "gh"


def check_repo(token: str, full_name: str) -> dict:
    from github import Auth, Github
    from github.GithubException import GithubException

    client = Github(auth=Auth.Token(token), timeout=20, retry=2)

    try:
        user = client.get_user()
        login = user.login
    except GithubException as exc:
        raise PreflightError(
            "auth",
            f"token 无效或已过期: HTTP {exc.status}",
            "重新生成 token 并 export GITHUB_TOKEN=<新 token>",
        ) from exc

    try:
        repo = client.get_repo(full_name)
    except GithubException as exc:
        if exc.status == 404:
            raise PreflightError(
                "repo",
                f"仓库不可达: {full_name}（HTTP 404）",
                "私有仓库在无权限时同样返回 404，先确认路径拼写，再确认 token 具备 repo 读权限",
            ) from exc
        if exc.status == 403:
            raise PreflightError(
                "repo",
                "触发访问限制或 API 速率限制（HTTP 403）",
                "查看 X-RateLimit-Reset 后重试，或换用权限更完整的 token",
            ) from exc
        raise PreflightError(
            "repo", f"访问仓库失败: HTTP {exc.status} {exc.data}", "检查 token 权限范围"
        ) from exc

    return {
        "repo": repo.full_name,
        "default_branch": repo.default_branch,
        "private": repo.private,
        "authenticated_as": login,
        "permissions": {
            "push": bool(getattr(repo.permissions, "push", False)),
            "admin": bool(getattr(repo.permissions, "admin", False)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub 仓库前置检查")
    parser.add_argument("--repo", required=True, help="目标仓库，格式 owner/repo")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON，便于管道处理")
    args = parser.parse_args()

    try:
        python_version = check_python()
        pygithub_version = check_pygithub()
        token, token_source = resolve_token()
        info = check_repo(token, args.repo)
    except PreflightError as exc:
        payload = {
            "ok": False,
            "stage": exc.stage,
            "error": exc.message,
            "hint": exc.hint,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    info.update(
        {
            "ok": True,
            "python": python_version,
            "pygithub": pygithub_version,
            "token_source": token_source,
        }
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
