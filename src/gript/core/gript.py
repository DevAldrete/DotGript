"""
Enterprise-Grade Git Automation Suite - Complete Implementation
Comprehensive Git automations following GitHub Flow, GitFlow, and enterprise best practices
Perfect for DotGript integration and general DevOps workflows
"""

import os
import re
import json
import time
import glob
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

# External dependencies for enhanced functionality
import semver
import yaml
import toml
from git import Repo, InvalidGitRepositoryError, GitCommandError
from git.objects import Commit
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

console = Console()


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
    pre_commit_hooks: bool = True
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


class GitAutomationSuite:
    """Enterprise-grade Git automation suite with complete functionality"""

    def __init__(self, repo_path: str = ".", config: AutomationConfig = None):
        try:
            self.repo = Repo(repo_path)
            self.config = config or AutomationConfig()
            self.branch_strategy = self.config.branch_strategy
            self.console = Console()
            self._setup_environment()
        except InvalidGitRepositoryError:
            raise ValueError(f"Invalid Git repository: {repo_path}")

    def _setup_environment(self):
        """Initialize the automation environment"""
        # Create config directory
        config_dir = Path(self.repo.working_dir) / ".gript"
        config_dir.mkdir(exist_ok=True)

        # Save configuration
        config_file = config_dir / "config.json"
        self._save_config(config_file)

        # Setup pre-commit hooks if enabled
        if self.config.pre_commit_hooks:
            self._setup_pre_commit_hooks()

    def _save_config(self, config_file: Path):
        """Save current configuration to file"""
        config_dict = {
            "workflow_type": self.config.workflow_type.value,
            "branch_strategy": {
                "main_branch": self.branch_strategy.main_branch,
                "develop_branch": self.branch_strategy.develop_branch,
                "feature_prefix": self.branch_strategy.feature_prefix,
                "hotfix_prefix": self.branch_strategy.hotfix_prefix,
                "release_prefix": self.branch_strategy.release_prefix,
                "bugfix_prefix": self.branch_strategy.bugfix_prefix,
            },
            "enforce_conventional_commits": self.config.enforce_conventional_commits,
            "auto_squash_merge": self.config.auto_squash_merge,
            "semantic_versioning": self.config.semantic_versioning,
            "auto_changelog": self.config.auto_changelog,
            "protected_branches": self.config.protected_branches,
            "max_commit_message_length": self.config.max_commit_message_length,
        }

        with open(config_file, "w") as f:
            json.dump(config_dict, f, indent=2)

    def _setup_pre_commit_hooks(self):
        """Setup pre-commit hooks for validation"""
        hooks_dir = Path(self.repo.git_dir) / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        pre_commit_hook = hooks_dir / "pre-commit"
        hook_content = """#!/bin/sh
# DotGript pre-commit hook
python -c "
import sys
sys.path.append('.')
from git_automation_suite import GitAutomationSuite
suite = GitAutomationSuite()
result = suite.validate_commit_message()
if not result['valid']:
    print(f'Commit message validation failed: {result[\"error\"]}')
    sys.exit(1)
"
"""
        pre_commit_hook.write_text(hook_content)
        pre_commit_hook.chmod(0o755)

    # ====================
    # SMART FEATURE BRANCH WORKFLOWS (Enhanced)
    # ====================

    def smart_feature_start(
        self,
        feature_name: str,
        issue_number: Optional[int] = None,
        from_branch: Optional[str] = None,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """Enhanced intelligent feature branch creation with context awareness"""

        if interactive:
            feature_name = self._interactive_feature_naming(feature_name, issue_number)

        # Sanitize feature name
        feature_name = self._sanitize_branch_name(feature_name)

        # Determine base branch
        base_branch = from_branch or self._get_base_branch_for_workflow()

        # Generate branch name based on workflow
        branch_name = self._generate_branch_name(feature_name, issue_number, "feature")

        # Check if branch already exists
        if branch_name in [b.name for b in self.repo.branches]:
            return {
                "success": False,
                "error": f"Branch '{branch_name}' already exists",
                "suggestion": f"{branch_name}-{int(time.time())}",
            }

        # Ensure we're on the correct base branch and it's up to date
        self._ensure_branch_updated(base_branch)

        # Create and switch to feature branch
        feature_branch = self.repo.create_head(branch_name)
        feature_branch.checkout()

        # Set upstream tracking
        upstream_set = False
        if self.repo.remotes:
            try:
                self.repo.git.push("--set-upstream", "origin", branch_name)
                upstream_set = True
            except GitCommandError:
                pass  # Remote might not exist yet

        # Create branch metadata
        self._create_branch_metadata(
            branch_name,
            {
                "type": "feature",
                "base_branch": base_branch,
                "created_at": datetime.now().isoformat(),
                "issue_number": issue_number,
                "description": feature_name.replace("-", " ").title(),
            },
        )

        return {
            "success": True,
            "branch_name": branch_name,
            "base_branch": base_branch,
            "upstream_set": upstream_set,
            "created_at": datetime.now().isoformat(),
        }

    def smart_feature_finish(
        self,
        branch_name: Optional[str] = None,
        squash: Optional[bool] = None,
        delete_branch: Optional[bool] = None,
        push_after_merge: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced intelligent feature branch completion"""

        # Use current branch if not specified
        if branch_name is None:
            branch_name = self.repo.active_branch.name

        squash = squash if squash is not None else self.config.auto_squash_merge
        delete_branch = (
            delete_branch
            if delete_branch is not None
            else self.config.auto_delete_merged_branches
        )

        # Validate current state
        if self.repo.is_dirty():
            return {
                "success": False,
                "error": "Repository has uncommitted changes",
                "suggestion": "Commit or stash your changes first",
            }

        # Get branch metadata
        branch_metadata = self._get_branch_metadata(branch_name)

        # Determine target branch
        target_branch = self._get_target_branch_for_workflow(branch_metadata)

        # Ensure target branch is updated
        self._ensure_branch_updated(target_branch)

        # Perform merge
        self.repo.heads[target_branch].checkout()

        merge_result = {
            "branch": branch_name,
            "target": target_branch,
            "squashed": squash,
            "timestamp": datetime.now().isoformat(),
            "commits_merged": [],
        }

        try:
            # Get commits that will be merged
            commits = list(self.repo.iter_commits(f"{target_branch}..{branch_name}"))
            merge_result["commits_merged"] = [c.hexsha for c in commits]

            if squash:
                self.repo.git.merge("--squash", branch_name)
                # Create squash commit with conventional commit format
                commit_msg = self._generate_squash_commit_message(branch_name, commits)
                commit = self.repo.index.commit(commit_msg)
                merge_result["commit_message"] = commit_msg
                merge_result["merge_commit"] = commit.hexsha
            else:
                merge_commit = self.repo.git.merge(
                    "--no-ff",
                    branch_name,
                    "-m",
                    f"Merge branch '{branch_name}' into {target_branch}",
                )
                merge_result["merge_commit"] = self.repo.head.commit.hexsha

            # Push changes if requested
            if push_after_merge and self.repo.remotes:
                try:
                    self.repo.remotes.origin.push()
                    merge_result["pushed"] = True
                except GitCommandError as e:
                    merge_result["push_error"] = str(e)

            # Delete feature branch if configured
            if delete_branch:
                self.repo.delete_head(branch_name)
                merge_result["branch_deleted"] = True

                # Delete remote branch too
                if self.repo.remotes:
                    try:
                        self.repo.remotes.origin.push("--delete", branch_name)
                        merge_result["remote_branch_deleted"] = True
                    except GitCommandError:
                        pass

            # Clean up branch metadata
            self._delete_branch_metadata(branch_name)

            merge_result["success"] = True

        except GitCommandError as e:
            merge_result["success"] = False
            merge_result["error"] = str(e)

            # Attempt conflict resolution if configured
            if (
                "CONFLICT" in str(e)
                and self.config.conflict_resolution != ConflictResolution.MANUAL
            ):
                resolution_result = self._auto_resolve_conflicts()
                merge_result["conflict_resolution"] = resolution_result

        return merge_result

    def list_active_features(self) -> List[Dict[str, Any]]:
        """List all active feature branches with metadata"""
        features = []

        for branch in self.repo.branches:
            if branch.name.startswith(self.branch_strategy.feature_prefix):
                metadata = self._get_branch_metadata(branch.name)

                # Get branch info
                branch_info = self._get_branch_info(branch.name)

                feature_data = {
                    "name": branch.name,
                    "display_name": branch.name.replace(
                        self.branch_strategy.feature_prefix, ""
                    ),
                    "created_at": metadata.get("created_at"),
                    "issue_number": metadata.get("issue_number"),
                    "description": metadata.get("description"),
                    "base_branch": metadata.get("base_branch"),
                    "ahead": branch_info.ahead,
                    "behind": branch_info.behind,
                    "last_commit": branch_info.last_commit,
                    "last_commit_date": branch_info.last_commit_date.isoformat(),
                    "is_stale": branch_info.is_stale,
                }

                features.append(feature_data)

        return sorted(features, key=lambda x: x["last_commit_date"], reverse=True)

    # ====================
    # INTELLIGENT COMMIT WORKFLOWS (Enhanced)
    # ====================

    def smart_commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        commit_type: Optional[ConventionalCommitType] = None,
        scope: Optional[str] = None,
        breaking_change: bool = False,
        auto_stage: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced intelligent commit with comprehensive validation"""

        # Auto-detect files if not specified
        if files is None and auto_stage:
            files = self._get_changed_files()
        elif files is None:
            files = self._get_staged_files()

        if not files:
            return {"success": False, "error": "No files to commit"}

        # Validate commit message
        validation_result = self._validate_commit_message(
            message, commit_type, scope, breaking_change
        )
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Stage files if auto_stage is enabled
        if auto_stage:
            self.repo.index.add(files)

        # Format commit message
        formatted_message = self._format_commit_message(
            message, commit_type, scope, breaking_change
        )

        # Pre-commit validation
        pre_commit_result = self._run_pre_commit_hooks(files)
        if not pre_commit_result["success"]:
            return {
                "success": False,
                "error": f"Pre-commit hook failed: {pre_commit_result['error']}",
            }

        # Commit with metadata
        try:
            commit = self.repo.index.commit(formatted_message)

            # Post-commit actions
            self._post_commit_actions(commit, files)

            return {
                "success": True,
                "commit_sha": commit.hexsha,
                "short_sha": commit.hexsha[:8],
                "message": formatted_message,
                "files": files,
                "insertions": self._count_insertions(commit),
                "deletions": self._count_deletions(commit),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def intelligent_commit_suggestions(self) -> List[Dict[str, Any]]:
        """AI-powered commit message suggestions based on file changes"""
        suggestions = []
        changed_files = self._get_changed_files_with_status()

        if not changed_files:
            return suggestions

        # Group files by type and change pattern
        file_groups = self._group_files_by_pattern(changed_files)

        for group_type, files in file_groups.items():
            suggestion = {
                "type": group_type,
                "files": files,
                "suggested_commit_type": self._suggest_commit_type_for_group(
                    group_type, files
                ),
                "suggested_scope": self._suggest_scope(files),
                "suggested_messages": self._generate_commit_messages(group_type, files),
                "confidence": self._calculate_suggestion_confidence(group_type, files),
            }
            suggestions.append(suggestion)

        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)

    def commit_with_ai_suggestion(self, accept_first: bool = False) -> Dict[str, Any]:
        """Commit using AI suggestions with optional user interaction"""
        suggestions = self.intelligent_commit_suggestions()

        if not suggestions:
            return {"success": False, "error": "No changes to commit"}

        if accept_first or len(suggestions) == 1:
            selected = suggestions[0]
        else:
            # Interactive selection
            selected = self._interactive_commit_selection(suggestions)
            if not selected:
                return {"success": False, "error": "No suggestion selected"}

        # Use the selected suggestion
        return self.smart_commit(
            message=selected["suggested_messages"][0],
            files=selected["files"],
            commit_type=selected["suggested_commit_type"],
        )

    def validate_commit_message(self, message: Optional[str] = None) -> Dict[str, Any]:
        """Validate commit message against configured rules"""
        if message is None:
            # Get the last commit message for validation
            try:
                message = self.repo.head.commit.message.strip()
            except:
                return {"valid": False, "error": "No commit message to validate"}

        return self._validate_commit_message(message)

    # ====================
    # RELEASE MANAGEMENT AUTOMATION (Enhanced)
    # ====================

    def smart_release(
        self,
        version_bump: str = "patch",
        pre_release: bool = False,
        release_notes: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Enhanced intelligent semantic versioning and release automation"""

        if not self.config.semantic_versioning:
            return {
                "success": False,
                "error": "Semantic versioning not enabled in configuration",
            }

        # Get current version
        current_version = self._get_current_version()

        # Calculate next version
        try:
            new_version = self._calculate_next_version(
                current_version, version_bump, pre_release
            )
        except Exception as e:
            return {"success": False, "error": f"Version calculation failed: {str(e)}"}

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "current_version": current_version,
                "new_version": new_version,
                "changes_preview": self._generate_changelog_preview(current_version),
            }

        # Validate release state
        validation = self._validate_release_state()
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        # Create release branch for GitFlow
        release_branch = None
        if self.config.workflow_type == WorkflowType.GITFLOW:
            release_branch = f"{self.branch_strategy.release_prefix}{new_version}"
            self._ensure_branch_updated(self.branch_strategy.develop_branch)
            self.repo.create_head(release_branch).checkout()

        try:
            # Generate changelog
            changelog = self._generate_changelog(current_version, new_version)

            # Update version files
            version_files_updated = self._update_version_files(new_version)

            # Update changelog file
            self._update_changelog_file(changelog, new_version)

            # Stage version changes
            files_to_commit = version_files_updated + ["CHANGELOG.md"]
            self.repo.index.add(files_to_commit)

            # Commit version bump
            version_commit = self.repo.index.commit(
                f"chore: bump version to {new_version}"
            )

            # Create annotated tag
            tag_message = release_notes or f"Release {new_version}\n\n{changelog}"
            tag = self.repo.create_tag(
                f"v{new_version}", message=tag_message, force=True
            )

            release_info = {
                "success": True,
                "version": new_version,
                "previous_version": current_version,
                "tag": tag.name,
                "commit": version_commit.hexsha,
                "changelog": changelog,
                "files_updated": files_to_commit,
                "timestamp": datetime.now().isoformat(),
            }

            # Merge back to main/master if GitFlow
            if self.config.workflow_type == WorkflowType.GITFLOW and release_branch:
                merge_result = self._merge_release_to_main(release_branch, new_version)
                release_info["merge_result"] = merge_result

            # Push tags and branches
            if self.repo.remotes:
                try:
                    self.repo.remotes.origin.push()
                    self.repo.remotes.origin.push("--tags")
                    release_info["pushed"] = True
                except GitCommandError as e:
                    release_info["push_error"] = str(e)

            return release_info

        except Exception as e:
            return {"success": False, "error": f"Release failed: {str(e)}"}

    def hotfix_workflow(
        self,
        hotfix_name: str,
        target_version: Optional[str] = None,
        from_tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced emergency hotfix workflow for production issues"""

        hotfix_name = self._sanitize_branch_name(hotfix_name)
        hotfix_branch = f"{self.branch_strategy.hotfix_prefix}{hotfix_name}"

        # Determine base for hotfix
        if from_tag:
            base_commit = self.repo.tags[from_tag].commit
        else:
            base_commit = self.repo.heads[self.branch_strategy.main_branch].commit

        # Create hotfix branch
        self.repo.create_head(hotfix_branch, base_commit).checkout()

        # Calculate target version if not provided
        if not target_version:
            current_version = self._get_current_version()
            target_version = self._calculate_next_version(current_version, "patch")

        # Create branch metadata
        self._create_branch_metadata(
            hotfix_branch,
            {
                "type": "hotfix",
                "base_branch": self.branch_strategy.main_branch,
                "base_commit": base_commit.hexsha,
                "target_version": target_version,
                "created_at": datetime.now().isoformat(),
                "description": f"Hotfix: {hotfix_name.replace('-', ' ').title()}",
            },
        )

        return {
            "success": True,
            "hotfix_branch": hotfix_branch,
            "base_branch": self.branch_strategy.main_branch,
            "base_commit": base_commit.hexsha,
            "target_version": target_version,
            "created_at": datetime.now().isoformat(),
        }

    def finish_hotfix(self, hotfix_branch: Optional[str] = None) -> Dict[str, Any]:
        """Complete hotfix workflow with automatic merging to main and develop"""

        if hotfix_branch is None:
            hotfix_branch = self.repo.active_branch.name

        if not hotfix_branch.startswith(self.branch_strategy.hotfix_prefix):
            return {"success": False, "error": "Not currently on a hotfix branch"}

        # Get hotfix metadata
        metadata = self._get_branch_metadata(hotfix_branch)
        target_version = metadata.get("target_version")

        if not target_version:
            return {"success": False, "error": "No target version found for hotfix"}

        try:
            # Update version files
            version_files = self._update_version_files(target_version)

            # Commit version update
            self.repo.index.add(version_files)
            version_commit = self.repo.index.commit(
                f"chore: bump version to {target_version}"
            )

            # Create tag
            tag = self.repo.create_tag(
                f"v{target_version}", message=f"Hotfix release {target_version}"
            )

            # Merge to main
            self.repo.heads[self.branch_strategy.main_branch].checkout()
            self.repo.git.merge("--no-ff", hotfix_branch)

            # Merge to develop if it exists
            merge_to_develop = False
            if self.branch_strategy.develop_branch in [
                b.name for b in self.repo.branches
            ]:
                self.repo.heads[self.branch_strategy.develop_branch].checkout()
                self.repo.git.merge("--no-ff", self.branch_strategy.main_branch)
                merge_to_develop = True

            # Clean up
            self.repo.delete_head(hotfix_branch)
            self._delete_branch_metadata(hotfix_branch)

            return {
                "success": True,
                "version": target_version,
                "tag": tag.name,
                "merged_to_main": True,
                "merged_to_develop": merge_to_develop,
                "hotfix_branch_deleted": True,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ====================
    # HELPER METHODS
    # ====================

    def _interactive_feature_naming(
        self, initial_name: str, issue_number: Optional[int]
    ) -> str:
        """Interactive feature naming with suggestions"""
        self.console.print("\n[bold blue]Feature Branch Creation[/bold blue]")

        # Show current suggestion
        suggested_name = self._sanitize_branch_name(initial_name)
        self.console.print(f"Suggested name: [green]{suggested_name}[/green]")

        # Get user input
        from rich.prompt import Prompt

        final_name = Prompt.ask(
            "Enter feature name (or press Enter to use suggestion)",
            default=suggested_name,
        )

        return final_name

    def _get_base_branch_for_workflow(self) -> str:
        """Get the appropriate base branch for the current workflow"""
        if self.config.workflow_type == WorkflowType.GITFLOW:
            return self.branch_strategy.develop_branch
        else:
            return self.branch_strategy.main_branch

    def _generate_branch_name(
        self, name: str, issue_number: Optional[int], branch_type: str
    ) -> str:
        """Generate branch name based on workflow and conventions"""
        if self.config.workflow_type == WorkflowType.GITHUB_FLOW:
            if issue_number:
                return f"{issue_number}-{name}"
            return name
        else:
            prefix = getattr(self.branch_strategy, f"{branch_type}_prefix")
            return f"{prefix}{name}"

    def _get_target_branch_for_workflow(self, branch_metadata: Dict) -> str:
        """Determine target branch for merge based on workflow and branch metadata"""
        if self.config.workflow_type == WorkflowType.GITFLOW:
            branch_type = branch_metadata.get("type")
            if branch_type == "hotfix":
                return self.branch_strategy.main_branch
            else:
                return self.branch_strategy.develop_branch
        else:
            return self.branch_strategy.main_branch

    def _create_branch_metadata(self, branch_name: str, metadata: Dict):
        """Create metadata file for branch tracking"""
        metadata_dir = Path(self.repo.working_dir) / ".gript" / "branches"
        metadata_dir.mkdir(exist_ok=True)

        metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def _get_branch_metadata(self, branch_name: str) -> Dict:
        """Get metadata for a branch"""
        metadata_dir = Path(self.repo.working_dir) / ".gript" / "branches"
        metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"

        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _delete_branch_metadata(self, branch_name: str):
        """Delete metadata for a branch"""
        metadata_dir = Path(self.repo.working_dir) / ".gript" / "branches"
        metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"

        if metadata_file.exists():
            metadata_file.unlink()

    def _get_branch_info(self, branch_name: str) -> BranchInfo:
        """Get comprehensive information about a branch"""
        branch = self.repo.heads[branch_name]

        # Calculate ahead/behind
        ahead, behind = 0, 0
        tracking_branch = None

        if branch.tracking_branch():
            tracking_branch = branch.tracking_branch().name
            try:
                ahead, behind = self.repo.git.rev_list(
                    "--left-right", "--count", f"{tracking_branch}...{branch_name}"
                ).split("\t")
                ahead, behind = int(ahead), int(behind)
            except:
                pass

        # Check if branch is merged
        is_merged = False
        try:
            self.repo.git.merge_base(
                "--is-ancestor", branch_name, self.branch_strategy.main_branch
            )
            is_merged = True
        except GitCommandError:
            pass

        # Check if branch is stale (older than 30 days)
        last_commit_date = branch.commit.committed_datetime
        is_stale = (datetime.now() - last_commit_date.replace(tzinfo=None)).days
