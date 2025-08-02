"""
Configuration and data models for Gript automations.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class WorkflowType(Enum):
    GITHUB_FLOW = "github_flow"
    GITFLOW = "gitflow"
    GITLAB_FLOW = "gitlab_flow"
    CUSTOM = "custom"


class ConventionalCommitType(Enum):
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    CHORE = "chore"
    CI = "ci"
    BUILD = "build"
    REVERT = "revert"


class MergeStrategy(Enum):
    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


class ConflictResolution(Enum):
    MANUAL = "manual"
    OURS = "ours"
    THEIRS = "theirs"
    AUTO = "auto"


@dataclass
class BranchStrategy:
    main_branch: str = "main"
    develop_branch: str = "develop"
    feature_prefix: str = "feature/"
    hotfix_prefix: str = "hotfix/"
    release_prefix: str = "release/"
    bugfix_prefix: str = "bugfix/"
    support_prefix: str = "support/"


@dataclass
class AutomationConfig:
    workflow_type: WorkflowType = WorkflowType.GITHUB_FLOW
    branch_strategy: BranchStrategy = field(default_factory=BranchStrategy)
    enforce_conventional_commits: bool = True
    auto_squash_merge: bool = True
    require_pr_review: bool = True
    auto_delete_merged_branches: bool = True
    semantic_versioning: bool = True
    auto_changelog: bool = True
    conflict_resolution: ConflictResolution = ConflictResolution.MANUAL
    merge_strategy: MergeStrategy = MergeStrategy.SQUASH
    protected_branches: List[str] = field(
        default_factory=lambda: ["main", "master", "develop"]
    )
    commit_message_template: Optional[str] = None
    max_commit_message_length: int = 72
    require_signed_commits: bool = False


@dataclass
class CommitAnalysis:
    sha: str
    message: str
    author: str
    date: datetime
    files_changed: List[str]
    insertions: int
    deletions: int
    commit_type: Optional[ConventionalCommitType]
    breaking_change: bool = False
    scope: Optional[str] = None


@dataclass
class BranchInfo:
    name: str
    tracking_branch: Optional[str]
    ahead: int
    behind: int
    last_commit: str
    last_commit_date: datetime
    is_merged: bool
    is_stale: bool
