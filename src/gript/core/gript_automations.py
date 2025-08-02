"""
Enterprise-Grade Git Automation Suite - Complete Implementation
Comprehensive Git automations following GitHub Flow, GitFlow, and enterprise best practices
Perfect for DotGript integration and general DevOps workflows
"""
from pathlib import Path
from typing import Optional, Any, List, Dict

from git import Repo, InvalidGitRepositoryError
from rich.console import Console

from .automations.config import AutomationConfig
from .automations.feature import FeatureWorkflow
from .automations.commit import CommitWorkflow
from .automations.release import ReleaseWorkflow


class GitAutomationSuite:
    """Enterprise-grade Git automation suite with complete functionality"""

    def __init__(self, repo_path: str = ".", config: Optional[AutomationConfig] = None):
        try:
            self.repo = Repo(repo_path)
            self.config = config or AutomationConfig()
            self.console = Console()
            self._setup_environment()

            self.feature_workflow = FeatureWorkflow(self.repo, self.config)
            self.commit_workflow = CommitWorkflow(self.repo, self.config)
            self.release_workflow = ReleaseWorkflow(self.repo, self.config)

        except InvalidGitRepositoryError:
            raise ValueError(f"Invalid Git repository: {repo_path}")

    def _setup_environment(self):
        """Initialize the automation environment"""
        # Create config directory
        config_dir = Path(self.repo.working_dir) / ".gript"
        config_dir.mkdir(exist_ok=True)

        # Save configuration
        config_file = config_dir / ".conf.json"
        self._save_config(config_file)

    def _save_config(self, config_file: Path):
        """Save current configuration to file"""
        import json
        config_dict = {
            "workflow_type": self.config.workflow_type.value,
            "branch_strategy": {
                "main_branch": self.config.branch_strategy.main_branch,
                "develop_branch": self.config.branch_strategy.develop_branch,
                "feature_prefix": self.config.branch_strategy.feature_prefix,
                "hotfix_prefix": self.config.branch_strategy.hotfix_prefix,
                "release_prefix": self.config.branch_strategy.release_prefix,
                "bugfix_prefix": self.config.branch_strategy.bugfix_prefix,
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

    # ====================
    # SMART FEATURE BRANCH WORKFLOWS
    # ====================

    def smart_feature_start(
        self,
        feature_name: str,
        issue_number: Optional[int] = None,
        from_branch: Optional[str] = None,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """Enhanced intelligent feature branch creation with context awareness"""
        return self.feature_workflow.start(feature_name, issue_number, from_branch, interactive)

    def smart_feature_finish(
        self,
        branch_name: Optional[str] = None,
        squash: Optional[bool] = None,
        delete_branch: Optional[bool] = None,
        push_after_merge: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced intelligent feature branch completion"""
        return self.feature_workflow.finish(branch_name, squash, delete_branch, push_after_merge)

    def list_active_features(self) -> List[Dict[str, Any]]:
        """List all active feature branches with metadata"""
        return self.feature_workflow.list_active()

    # ====================
    # INTELLIGENT COMMIT WORKFLOWS (Enhanced)
    # ====================

    def smart_commit(
        self,
        message: str,
        files: Optional[List[str | None]] = None,
        commit_type: Optional[Any] = None,
        scope: Optional[str] = None,
        breaking_change: bool = False,
        auto_stage: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced intelligent commit with comprehensive validation"""
        return self.commit_workflow.smart_commit(message, files, commit_type, scope, breaking_change, auto_stage)

    def intelligent_commit_suggestions(self) -> List[Dict[str, Any]]:
        """AI-powered commit message suggestions based on file changes"""
        return self.commit_workflow.suggest()

    def commit_with_ai_suggestion(self, accept_first: bool = False) -> Dict[str, Any]:
        """Commit using AI suggestions with optional user interaction"""
        return self.commit_workflow.commit_with_suggestion(accept_first)

    def validate_commit_message(
        self, message: Optional[str | bytes] = None
    ) -> Dict[str, Any]:
        """Validate commit message against configured rules"""
        return self.commit_workflow.validate_message(message)

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
        return self.release_workflow.start_release(version_bump, pre_release, release_notes, dry_run)

    def hotfix_workflow(
        self,
        hotfix_name: str,
        target_version: Optional[str] = None,
        from_tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced emergency hotfix workflow for production issues"""
        return self.release_workflow.start_hotfix(hotfix_name, target_version, from_tag)

    def finish_hotfix(self, hotfix_branch: Optional[str] = None) -> Dict[str, Any]:
        """Complete hotfix workflow with automatic merging to main and develop"""
        return self.release_workflow.finish_hotfix(hotfix_branch)
