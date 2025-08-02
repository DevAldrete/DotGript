"""
Feature branch workflow automations.
"""
import time
from datetime import datetime
from typing import Any, Dict, Optional, List

from git import GitCommandError, Repo

from . import utils
from .config import AutomationConfig


class FeatureWorkflow:
    def __init__(self, repo: Repo, config: AutomationConfig):
        self.repo = repo
        self.config = config
        self.branch_strategy = config.branch_strategy

    def start(
        self,
        feature_name: str,
        issue_number: Optional[int] = None,
        from_branch: Optional[str] = None,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """Enhanced intelligent feature branch creation with context awareness"""

        if interactive:
            feature_name = utils.interactive_feature_naming(feature_name, issue_number)

        # Sanitize feature name
        feature_name = utils.sanitize_branch_name(feature_name)

        # Determine base branch
        base_branch = from_branch or utils.get_base_branch_for_workflow(self.config)

        # Generate branch name based on workflow
        branch_name = utils.generate_branch_name(self.config, feature_name, issue_number, "feature")

        # Check if branch already exists
        if branch_name in [b.name for b in self.repo.branches]:
            return {
                "success": False,
                "error": f"Branch '{branch_name}' already exists",
                "suggestion": f"{branch_name}-{int(time.time())}",
            }

        # Ensure we're on the correct base branch and it's up to date
        utils.ensure_branch_updated(self.repo, base_branch)

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
        utils.create_branch_metadata(
            self.repo,
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

    def finish(
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
        branch_metadata = utils.get_branch_metadata(self.repo, branch_name)

        # Determine target branch
        target_branch = utils.get_target_branch_for_workflow(self.config, branch_metadata)

        # Ensure target branch is updated
        utils.ensure_branch_updated(self.repo, target_branch)

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
                commit_msg = utils.generate_squash_commit_message(branch_name, commits)
                commit = self.repo.index.commit(commit_msg)
                merge_result["commit_message"] = commit_msg
                merge_result["merge_commit"] = commit.hexsha
            else:
                self.repo.git.merge(
                    "--no-ff",
                    branch_name,
                    "-m",
                    f"Merge branch '{branch_name}' into {target_branch}",
                )
                merge_result["merge_commit"] = self.repo.head.commit.hexsha

            # Push changes if requested
            if push_after_merge and self.repo.remotes:
                try:
                    self.repo.remotes.origin.push(target_branch)
                except GitCommandError as e:
                    merge_result["push_error"] = str(e)

            # Delete feature branch if configured
            if delete_branch:
                self.repo.delete_head(branch_name)
                merge_result["branch_deleted"] = True

                # Delete remote branch too
                if self.repo.remotes:
                    try:
                        self.repo.git.push("origin", "--delete", branch_name)
                    except GitCommandError:
                        pass  # May have already been deleted

            # Clean up branch metadata
            utils.delete_branch_metadata(self.repo, branch_name)

            merge_result["success"] = True

        except GitCommandError as e:
            merge_result["success"] = False
            merge_result["error"] = str(e)

            # Attempt conflict resolution if configured
            if (
                "CONFLICT" in str(e)
                and self.config.conflict_resolution != "manual"
            ):
                resolution_result = utils.auto_resolve_conflicts(self.repo, self.config)
                merge_result["conflict_resolution"] = resolution_result

        return merge_result

    def list_active(self) -> List[Dict[str, Any]]:
        """List all active feature branches with metadata"""
        features = []

        for branch in self.repo.branches:
            if branch.name.startswith(self.branch_strategy.feature_prefix):
                metadata = utils.get_branch_metadata(self.repo, branch.name)

                # Get branch info
                branch_info = utils.get_branch_info(self.repo, branch.name)

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
