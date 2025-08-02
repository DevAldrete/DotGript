"""
Release and hotfix workflow automations.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from git import GitCommandError, Repo

from . import utils
from .config import AutomationConfig, WorkflowType


class ReleaseWorkflow:
    def __init__(self, repo: Repo, config: AutomationConfig):
        self.repo = repo
        self.config = config
        self.branch_strategy = config.branch_strategy

    def start_release(
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
        current_version = utils.get_current_version(self.repo)

        # Calculate next version
        try:
            new_version = utils.calculate_next_version(
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
                "changes_preview": utils.generate_changelog_preview(self.repo, current_version),
            }

        # Validate release state
        validation = utils.validate_release_state(self.repo, self.config)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        # Create release branch for GitFlow
        release_branch = None
        if self.config.workflow_type == WorkflowType.GITFLOW:
            release_branch = f"{self.branch_strategy.release_prefix}{new_version}"
            utils.ensure_branch_updated(self.repo, self.branch_strategy.develop_branch)
            self.repo.create_head(release_branch).checkout()

        try:
            # Generate changelog
            changelog = utils.generate_changelog(self.repo, current_version, new_version)

            # Update version files
            version_files_updated = utils.update_version_files(self.repo, new_version)

            # Update changelog file
            utils.update_changelog_file(self.repo, changelog, new_version)

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
                merge_result = utils.merge_release_to_main(self.repo, self.config, release_branch, new_version)
                release_info["merge_result"] = merge_result

            # Push tags and branches
            if self.repo.remotes:
                try:
                    self.repo.git.push("--tags")
                    if release_branch:
                        self.repo.git.push("origin", self.branch_strategy.main_branch)
                        self.repo.git.push("origin", self.branch_strategy.develop_branch)
                except GitCommandError as e:
                    release_info["push_error"] = str(e)

            return release_info

        except Exception as e:
            return {"success": False, "error": f"Release failed: {str(e)}"}

    def start_hotfix(
        self,
        hotfix_name: str,
        target_version: Optional[str] = None,
        from_tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced emergency hotfix workflow for production issues"""

        hotfix_name = utils.sanitize_branch_name(hotfix_name)
        hotfix_branch = f"{self.branch_strategy.hotfix_prefix}{hotfix_name}"

        # Determine base for hotfix
        if from_tag:
            base_commit = self.repo.tags[from_tag].commit
        else:
            base_commit = self.repo.heads[self.branch_strategy.main_branch].commit

        # Create hotfix branch
        self.repo.create_head(hotfix_branch, base_commit.hexsha).checkout()

        # Calculate target version if not provided
        if not target_version:
            current_version = utils.get_current_version(self.repo)
            target_version = utils.calculate_next_version(current_version, "patch")

        # Create branch metadata
        utils.create_branch_metadata(
            self.repo,
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
        metadata = utils.get_branch_metadata(self.repo, hotfix_branch)
        target_version = metadata.get("target_version")

        if not target_version:
            return {"success": False, "error": "No target version found for hotfix"}

        try:
            # Update version files
            version_files = utils.update_version_files(self.repo, target_version)

            # Commit version update
            self.repo.index.add(version_files)
            self.repo.index.commit(
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
            utils.delete_branch_metadata(self.repo, hotfix_branch)

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
