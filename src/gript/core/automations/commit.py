"""
Commit workflow automations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from git import Repo

from . import utils
from .config import AutomationConfig, ConventionalCommitType


class CommitWorkflow:
    def __init__(self, repo: Repo, config: AutomationConfig):
        self.repo = repo
        self.config = config

    def smart_commit(
        self,
        message: str,
        files: Optional[List[str | None]] = None,
        commit_type: Optional[ConventionalCommitType] = None,
        scope: Optional[str] = None,
        breaking_change: bool = False,
        auto_stage: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced intelligent commit with comprehensive validation"""

        # Auto-detect files if not specified
        if files is None and auto_stage:
            files = utils.get_changed_files(self.repo)
        elif files is None:
            files = utils.get_staged_files(self.repo)

        if not files:
            return {"success": False, "error": "No files to commit"}

        # Validate commit message
        validation_result = utils.validate_commit_message(
            self.config, message, commit_type, scope, breaking_change
        )
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Stage files if auto_stage is enabled
        if auto_stage:
            self.repo.index.add(files)

        # Format commit message
        formatted_message = utils.format_commit_message(
            self.config, message, commit_type, scope, breaking_change
        )

        # Commit with metadata
        try:
            commit = self.repo.index.commit(formatted_message)

            return {
                "success": True,
                "commit_sha": commit.hexsha,
                "short_sha": commit.hexsha[:8],
                "message": formatted_message,
                "files": files,
                "insertions": utils.count_insertions(commit),
                "deletions": utils.count_deletions(commit),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def suggest(self) -> List[Dict[str, Any]]:
        """AI-powered commit message suggestions based on file changes"""
        suggestions = []
        changed_files = utils.get_changed_files_with_status(self.repo)

        if not changed_files:
            return suggestions

        # Group files by type and change pattern
        file_groups = utils.group_files_by_pattern(changed_files)

        for group_type, files in file_groups.items():
            suggestion = {
                "type": group_type,
                "files": files,
                "suggested_commit_type": utils.suggest_commit_type_for_group(
                    group_type, files
                ),
                "suggested_scope": utils.suggest_scope(files),
                "suggested_messages": utils.generate_commit_messages(group_type, files),
                "confidence": utils.calculate_suggestion_confidence(group_type, files),
            }
            suggestions.append(suggestion)

        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)

    def commit_with_suggestion(self, accept_first: bool = False) -> Dict[str, Any]:
        """Commit using AI suggestions with optional user interaction"""
        suggestions = self.suggest()

        if not suggestions:
            return {"success": False, "error": "No changes to commit"}

        if accept_first or len(suggestions) == 1:
            selected = suggestions[0]
        else:
            # Interactive selection
            selected = utils.interactive_commit_selection(suggestions)
            if not selected:
                return {"success": False, "error": "No suggestion selected"}

        # Use the selected suggestion
        return self.smart_commit(
            message=selected["suggested_messages"][0],
            files=selected["files"],
            commit_type=selected["suggested_commit_type"],
        )

    def validate_message(
        self, message: Optional[str | bytes] = None
    ) -> Dict[str, Any]:
        """Validate commit message against configured rules"""
        if message is None:
            # Get the last commit message for validation
            try:
                message = self.repo.head.commit.message
            except Exception:
                return {
                    "valid": False,
                    "error": "No commit message to validate",
                }

        return utils.validate_commit_message(self.config, message)
