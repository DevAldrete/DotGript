"""
Utility functions for Gript automations.
"""
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from git import GitCommandError, Repo
from git.objects import Commit
from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from .config import AutomationConfig, BranchInfo, ConventionalCommitType, WorkflowType

console = Console()

# Branch utilities

def sanitize_branch_name(name: str) -> str:
    """Convert any string to a git-safe branch name."""
    name = re.sub(r"[^A-Za-z0-9\-_]+", "-", name).strip("-_")
    return re.sub(r"-+", "-", name).lower()

def ensure_branch_updated(repo: Repo, branch: str):
    """Checkout <branch>, pull latest, return to original branch."""
    original = repo.active_branch.name
    if branch not in [b.name for b in repo.branches]:
        raise ValueError(f"Branch '{branch}' does not exist locally")
    repo.heads[branch].checkout()
    if repo.remotes:
        try:
            repo.remotes.origin.pull(branch)
        except GitCommandError:
            pass  # Remote might not exist
    if repo.active_branch.name != original:
        repo.heads[original].checkout()

def get_changed_files(repo: Repo) -> List[str | None]:
    """Return list of unstaged and staged files that have modifications."""
    return [item.a_path for item in repo.index.diff(None)] + [
        item.a_path for item in repo.index.diff("HEAD")
    ]

def get_staged_files(repo: Repo) -> List[str | None]:
    """Return list of files currently staged for commit."""
    return [item.a_path for item in repo.index.diff("HEAD")]

def get_changed_files_with_status(repo: Repo) -> List[Dict[str, str]]:
    """Return list of dicts: {path, status, insertions, deletions}."""
    files = []
    for item in repo.index.diff(None, cached=False):
        if item.diff is not None:
            files.append(
                {
                    "path": item.a_path,
                    "status": item.change_type,
                    "insertions": item.diff.decode('utf-8', 'ignore').count("\n+"),
                    "deletions": item.diff.decode('utf-8', 'ignore').count("\n-"),
                }
            )
    return files

# Commit helpers

def validate_commit_message(
    config: AutomationConfig,
    message: str | bytes,
    commit_type: Optional[ConventionalCommitType] = None,
    scope: Optional[str] = None,
    breaking: bool = False,
) -> Dict[str, Any]:
    """Core logic for commit-message validation."""
    if isinstance(message, bytes):
        message = message.decode('utf-8')
        
    if config.enforce_conventional_commits:
        pattern = r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(!)?:( .+)$"
        match = re.match(pattern, str(message))
        if not match:
            return {
                "valid": False,
                "error": "Message must follow conventional-commit spec",
            }
        if breaking and not match.group("type").endswith("!"):
            return {"valid": False, "error": "Breaking change must end with '!'"}
    if len(message) > config.max_commit_message_length:
        return {"valid": False, "error": "Message too long"}
    return {"valid": True}

def format_commit_message(
    config: AutomationConfig,
    message: str,
    commit_type: Optional[ConventionalCommitType],
    scope: Optional[str],
    breaking: bool,
) -> str:
    """Return a fully-formatted commit line."""
    if not config.enforce_conventional_commits:
        return message
    prefix = commit_type.value if commit_type else "chore"
    scope_part = f"({scope})" if scope else ""
    bang = "!" if breaking else ""
    return f"{prefix}{scope_part}{bang}: {message}"

def count_insertions(commit: Commit) -> int:
    return commit.stats.total["insertions"]

def count_deletions(commit: Commit) -> int:
    return commit.stats.total["deletions"]

# AI-like suggestion helpers

def group_files_by_pattern(
    files: List[Dict[str, str]]
) -> Dict[str, List[str]]:
    """Bucket files by extension/type for smarter suggestions."""
    buckets = defaultdict(list)
    for f in files:
        ext = Path(f["path"]).suffix.lower()
        if ext in {".py", ".js", ".ts", ".java", ".go", ".rs"}:
            buckets["src"].append(f["path"])
        elif ext in {".json", ".yml", ".yaml", ".toml", ".ini"}:
            buckets["config"].append(f["path"])
        elif "test" in f["path"].lower():
            buckets["test"].append(f["path"])
        elif ext in {".md", ".rst"}:
            buckets["docs"].append(f["path"])
        else:
            buckets["misc"].append(f["path"])
    return dict(buckets)

def suggest_commit_type_for_group(
    group_type: str, files: List[str]
) -> ConventionalCommitType:
    """Heuristic mapping from file group to commit type."""
    mapping = {
        "src": ConventionalCommitType.FEAT,
        "test": ConventionalCommitType.TEST,
        "docs": ConventionalCommitType.DOCS,
        "config": ConventionalCommitType.CHORE,
        "misc": ConventionalCommitType.CHORE,
    }
    return mapping.get(group_type, ConventionalCommitType.CHORE)

def suggest_scope(files: List[str]) -> Optional[str]:
    """Guess a sensible scope (folder name or domain)."""
    try:
        # Use the most common root folder among changed files
        folders = [str(Path(f).parent) for f in files]
        return Counter(folders).most_common(1)[0][0]
    except IndexError:
        return None

def generate_commit_messages(group_type: str, files: List[str]) -> List[str]:
    """Return 2-3 message suggestions."""
    verbs = {
        "feat": "add",
        "fix": "correct",
        "docs": "update",
        "test": "add tests for",
        "chore": "update",
    }
    ctype = suggest_commit_type_for_group(group_type, files)
    verb = verbs.get(ctype.value, "update")
    base = f"{verb} {len(files)} {group_type} file(s)"
    return [
        base,
        f"{base} (refactor)",
        f"{base} and bump version",
    ]

def calculate_suggestion_confidence(
    group_type: str, files: List[str]
) -> float:
    """Naïve confidence score between 0 and 1."""
    # The more uniform the file types, the higher the confidence
    exts = {Path(f).suffix for f in files}
    return max(0.1, 1.0 - (len(exts) * 0.25))

def interactive_commit_selection(
    suggestions: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Prompt user to pick a suggestion."""
    table = Table(title="Commit Suggestions")
    table.add_column("#", justify="right")
    table.add_column("Type")
    table.add_column("Files")
    table.add_column("Message")
    table.add_column("Confidence")

    for idx, s in enumerate(suggestions, 1):
        table.add_row(
            str(idx),
            s["suggested_commit_type"].value,
            str(len(s["files"])),
            s["suggested_messages"][0],
            f"{s['confidence']:.2f}",
        )
    console.print(table)

    choice = IntPrompt.ask(
        "Pick suggestion # (0 to cancel)",
        choices=[str(i) for i in range(len(suggestions) + 1)],
    )
    return None if choice == 0 else suggestions[choice - 1]

# Version & changelog helpers

def get_current_version(repo: Repo) -> str:
    """Return current semver from package.json, pyproject.toml, or git tags."""
    # 1) pyproject.toml
    pyproject = Path(repo.working_dir) / "pyproject.toml"
    if pyproject.exists():
        data = toml.loads(pyproject.read_text())
        return str(data.get("tool", {}).get("poetry", {}).get("version", "0.1.0"))

    # 2) package.json
    pkg_json = Path(repo.working_dir) / "package.json"
    if pkg_json.exists():
        data = json.loads(pkg_json.read_text())
        return str(data.get("version", "0.1.0"))

    # 3) latest git tag
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    if tags:
        tag = tags[-1].name
        if tag.startswith("v"):
            tag = tag[1:]
        return str(tag)

    return "0.1.0"

def calculate_next_version(
    current: str, bump: str, pre: bool = False
) -> str:
    """Return next semver string."""
    import semver
    ver = semver.VersionInfo.parse(current)
    if pre:
        return str(ver.bump_prerelease("rc"))
    if bump == "major":
        return str(ver.bump_major())
    if bump == "minor":
        return str(ver.bump_minor())
    return str(ver.bump_patch())

def validate_release_state(repo: Repo, config: AutomationConfig) -> Dict[str, Any]:
    """Ensure repo is ready for release (clean, on correct branch, etc.)."""
    if repo.is_dirty():
        return {"valid": False, "error": "Working directory must be clean"}
    if repo.active_branch.name not in {
        config.branch_strategy.main_branch,
        config.branch_strategy.develop_branch,
    }:
        return {"valid": False, "error": "Must be on main or develop branch"}
    return {"valid": True}

def generate_changelog_preview(repo: Repo, from_version: str) -> str:
    """Return a short preview of changes since <from_version>."""
    try:
        commits = list(repo.iter_commits(f"v{from_version}..HEAD"))
        lines = [f"- {c.message.splitlines()[0]}" for c in commits]
        return "\n".join(lines[:10]) + ("\n..." if len(lines) > 10 else "")
    except Exception:
        return "Could not generate changelog preview."

def generate_changelog(repo: Repo, old: str, new: str) -> str:
    """Real changelog generator (simple for now)."""
    commits = list(repo.iter_commits(f"v{old}..HEAD"))
    grouped = defaultdict(list)
    for c in commits:
        msg = c.message.splitlines()[0]
        if msg.startswith("feat"):
            grouped["Features"].append(msg)
        elif msg.startswith("fix"):
            grouped["Bug fixes"].append(msg)
        else:
            grouped["Other"].append(msg)

    out = [f"## [{new}] – {datetime.now().strftime('%Y-%m-%d')}"]
    for section, items in grouped.items():
        out.append(f"### {section}")
        out.extend(f"- {i}" for i in items)
    return "\n".join(out)

def update_version_files(repo: Repo, version: str) -> List[str]:
    """Write new version to package.json / pyproject.toml and return list of changed files."""
    updated = []

    # pyproject.toml
    pyproject = Path(repo.working_dir) / "pyproject.toml"
    if pyproject.exists():
        data = toml.loads(pyproject.read_text())
        data["tool"]["poetry"]["version"] = version
        pyproject.write_text(toml.dumps(data))
        updated.append(str(pyproject))

    # package.json
    pkg_json = Path(repo.working_dir) / "package.json"
    if pkg_json.exists():
        data = json.loads(pkg_json.read_text())
        data["version"] = version
        pkg_json.write_text(json.dumps(data, indent=2))
        updated.append(str(pkg_json))

    return updated

def update_changelog_file(repo: Repo, content: str, version: str):
    """Prepend changelog content to CHANGELOG.md (create if absent)."""
    changelog_path = Path(repo.working_dir) / "CHANGELOG.md"
    header = "# Changelog\n\n"
    if changelog_path.exists():
        old = changelog_path.read_text()
        if old.startswith("# Changelog"):
            old = old[len(header) :].lstrip()
        new_content = header + content + "\n\n" + old
    else:
        new_content = header + content
    changelog_path.write_text(new_content)

def merge_release_to_main(
    repo: Repo, config: AutomationConfig, release_branch: str, version: str
) -> Dict[str, Any]:
    """Finish GitFlow release: merge release → main → tag → develop."""
    repo.heads[config.branch_strategy.main_branch].checkout()
    repo.git.merge("--no-ff", release_branch)
    return {"merged_to_main": True}

# Conflict resolution

def auto_resolve_conflicts(repo: Repo, config: AutomationConfig) -> Dict[str, Any]:
    """Very basic conflict resolver: choose ours/theirs/auto based on config."""
    if config.conflict_resolution == "ours":
        repo.git.checkout("--ours", ".")
    elif config.conflict_resolution == "theirs":
        repo.git.checkout("--theirs", ".")
    elif config.conflict_resolution == "auto":
        # Attempt merge tool auto-resolution
        try:
            repo.git.add(".")
            return {"resolved": True, "method": "auto"}
        except GitCommandError as e:
            return {"resolved": False, "error": str(e)}
    repo.git.add(".")
    return {"resolved": True, "method": config.conflict_resolution}

# Branch inspection

def get_branch_info(repo: Repo, branch_name: str) -> BranchInfo:
    """Return BranchInfo dataclass for given branch."""
    branch = repo.branches[branch_name]
    tracking = branch.tracking_branch()
    tracking_name = tracking.name if tracking else None

    # ahead/behind vs upstream
    if tracking:
        commits_ahead = list(repo.iter_commits(f"{tracking}..{branch}"))
        commits_behind = list(repo.iter_commits(f"{branch}..{tracking}"))
    else:
        commits_ahead = commits_behind = []

    last_commit = branch.commit
    is_merged = branch.commit in repo.iter_commits(
        "main" # assume main
    )
    stale_days = 30
    is_stale = (
        datetime.utcnow() - last_commit.committed_datetime.replace(tzinfo=None)
    ).days > stale_days

    return BranchInfo(
        name=branch_name,
        tracking_branch=tracking_name,
        ahead=len(commits_ahead),
        behind=len(commits_behind),
        last_commit=last_commit.hexsha,
        last_commit_date=last_commit.committed_datetime,
        is_merged=is_merged,
        is_stale=is_stale,
    )

def generate_squash_commit_message(
    branch_name: str, commits: List[Commit]
) -> str:
    """Produce a single squash commit message for a feature branch."""
    types = [c.message.split(":")[0].split("(")[0] for c in commits]
    most_common = Counter(types).most_common(1)[0][0]
    # Prefer feat/fix, fallback to most common
    commit_type = (
        ConventionalCommitType.FEAT
        if "feat" in types
        else ConventionalCommitType.FIX
        if "fix" in types
        else ConventionalCommitType(most_common)
    )
    feature_desc = branch_name.replace("-", " ").replace("_", " ").title()
    return f"{commit_type.value}: {feature_desc}"

def interactive_feature_naming(
    initial_name: str, issue_number: Optional[int]
) -> str:
    """Interactive feature naming with suggestions"""
    console.print("\n[bold blue]Feature Branch Creation[/bold blue]")

    # Show current suggestion
    suggested_name = sanitize_branch_name(initial_name)
    console.print(f"Suggested name: [green]{suggested_name}[/green]")

    # Get user input
    final_name = Prompt.ask(
        "Enter feature name (or press Enter to use suggestion)",
        default=suggested_name,
    )

    return final_name

def get_base_branch_for_workflow(config: AutomationConfig) -> str:
    """Get the appropriate base branch for the current workflow"""
    if config.workflow_type == WorkflowType.GITFLOW:
        return config.branch_strategy.develop_branch
    else:
        return config.branch_strategy.main_branch

def generate_branch_name(
    config: AutomationConfig, name: str, issue_number: Optional[int], branch_type: str
) -> str:
    """Generate branch name based on workflow and conventions"""
    if config.workflow_type == WorkflowType.GITHUB_FLOW:
        if issue_number:
            return f"{issue_number}-{name}"
        return name
    else:
        prefix = getattr(config.branch_strategy, f"{branch_type}_prefix")
        return f"{prefix}{name}"

def get_target_branch_for_workflow(config: AutomationConfig, branch_metadata: Dict) -> str:
    """Determine target branch for merge based on workflow and branch metadata"""
    if config.workflow_type == WorkflowType.GITFLOW:
        branch_type = branch_metadata.get("type")
        if branch_type == "hotfix":
            return config.branch_strategy.main_branch
        else:
            return config.branch_strategy.develop_branch
    else:
        return config.branch_strategy.main_branch

def create_branch_metadata(repo: Repo, branch_name: str, metadata: Dict):
    """Create metadata file for branch tracking"""
    metadata_dir = Path(repo.working_dir) / ".gript" / "branches"
    metadata_dir.mkdir(exist_ok=True)

    metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

def get_branch_metadata(repo: Repo, branch_name: str) -> Dict:
    """Get metadata for a branch"""
    metadata_dir = Path(repo.working_dir) / ".gript" / "branches"
    metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"

    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            return json.load(f)
    return {}

def delete_branch_metadata(repo: Repo, branch_name: str):
    """Delete metadata for a branch"""
    metadata_dir = Path(repo.working_dir) / ".gript" / "branches"
    metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"

    if metadata_file.exists():
        metadata_file.unlink()
