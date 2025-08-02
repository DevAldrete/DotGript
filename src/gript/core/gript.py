"""
Gript Git Module
This module provides a high-level interface to interact with Git repositories,
integrating with the DotGript automation system. It wraps basic Git operations
with automation features like configuration management and branch metadata tracking.
"""
from pathlib import Path
from datetime import datetime
from git import Repo
from typing import Optional, List, Dict, Any

from .gript import (
    branch,
    commit,
    remote,
    repository,
    errors
)

class GriptGit:
    """
    Enhanced Git operations class that integrates with DotGript automation system.
    This class wraps basic Git operations with automation features like configuration
    management, branch metadata tracking, and .gript folder integration.
    """
    
    def __init__(self, repo_path: str = ".", config: Optional[Any] = None):
        try:
            self.repo = Repo(repo_path, search_parent_directories=True)
        except Exception as e:
            raise errors.GitError("Initialization", str(e))
        
        self.config = config or {}
        self._ensure_gript_dir()
    
    def _ensure_gript_dir(self):
        """Ensure the .gript directory exists."""
        gript_dir = Path(self.repo.working_dir) / ".gript"
        gript_dir.mkdir(exist_ok=True)
    
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log the operation to a file in the .gript directory."""
        log_file = Path(self.repo.working_dir) / ".gript" / "operations.log"
        with log_file.open("a") as f:
            f.write(f"{datetime.now().isoformat()} - {operation}: {details}\n")
    
    def _update_operation_stats(self, operation: str):
        """Update operation statistics."""
        # Placeholder for more advanced stats tracking
        pass
    
    # Enhanced Git operations with automation integration
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None, 
                      amend: bool = False, allow_empty: bool = False,
                      use_conventional_commits: bool = True) -> str:
        """
        Commit changes with optional conventional commit formatting.
        """
        # Placeholder for conventional commit logic
        if use_conventional_commits:
            # This would be where you format the message
            pass
        
        commit_hash = commit.commit_changes(self.repo, message, files, amend, allow_empty)
        self._log_operation("commit", {"message": message, "files": files, "commit_hash": commit_hash})
        self._update_operation_stats("commit")
        return commit_hash
    
    def create_branch(self, branch_name: str, issue_number: Optional[int] = None,
                     from_branch: Optional[str] = None, interactive: bool = False) -> Dict[str, Any]:
        """
        Create a new branch with optional metadata.
        """
        # Placeholder for interactive branch creation
        if interactive:
            # This would be where you prompt the user for branch details
            pass
            
        branch.create_branch(self.repo, branch_name)
        
        metadata = {
            "issue_number": issue_number,
            "from_branch": from_branch or self.get_current_branch(),
            "created_at": datetime.now().isoformat()
        }
        self._save_branch_metadata(branch_name, metadata)
        
        self._log_operation("create_branch", {"branch_name": branch_name, "metadata": metadata})
        self._update_operation_stats("create_branch")
        
        return {"branch_name": branch_name, "metadata": metadata}
    
    def _save_branch_metadata(self, branch_name: str, metadata: Dict[str, Any]):
        """Save branch metadata to a file in the .gript directory."""
        metadata_dir = Path(self.repo.working_dir) / ".gript" / "branches"
        metadata_dir.mkdir(exist_ok=True)
        metadata_file = metadata_dir / f"{branch_name.replace('/', '_')}.json"
        import json
        with metadata_file.open("w") as f:
            json.dump(metadata, f, indent=4)
    
    def push_changes(self, remote_name: str = 'origin', branch_name: Optional[str] = None,
                    force: bool = False, set_upstream: bool = False) -> str:
        """Push changes to a remote repository."""
        result = remote.push_changes(self.repo, remote_name, branch_name, force, set_upstream)
        self._log_operation("push", {"remote": remote_name, "branch": branch_name, "result": result})
        self._update_operation_stats("push")
        return result
    
    def pull_changes(self, remote_name: str = 'origin', branch_name: Optional[str] = None,
                    rebase: bool = False) -> str:
        """Pull changes from a remote repository."""
        result = remote.pull_changes(self.repo, remote_name, branch_name, rebase)
        self._log_operation("pull", {"remote": remote_name, "branch": branch_name, "result": result})
        self._update_operation_stats("pull")
        return result
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        return branch.get_current_branch(self.repo)
    
    def get_repo_status(self) -> Dict[str, List[str]]:
        """Get the repository status."""
        return repository.get_repo_status(self.repo)
    
    def get_gript_info(self) -> Dict[str, Any]:
        """Get information about the Gript setup for this repository."""
        gript_dir = Path(self.repo.working_dir) / ".gript"
        return {
            "gript_directory_exists": gript_dir.exists(),
            "log_file_exists": (gript_dir / "operations.log").exists(),
            "branch_metadata_count": len(list((gript_dir / "branches").glob("*.json"))) if (gript_dir / "branches").exists() else 0
        }

# Factory and utility functions for enhanced Git operations

def create_gript_git(repo_path: str = ".", config: Optional[Any] = None) -> GriptGit:
    """Create a GriptGit instance."""
    return GriptGit(repo_path, config)

def setup_gript_automation(repo_path: str = ".", 
                          workflow_type: str = "github_flow",
                          enforce_conventional_commits: bool = True,
                          auto_squash_merge: bool = True) -> GriptGit:
    """
    Setup Gript automation for a repository.
    """
    # Placeholder for more complex setup logic
    config = {
        "workflow_type": workflow_type,
        "enforce_conventional_commits": enforce_conventional_commits,
        "auto_squash_merge": auto_squash_merge
    }
    return GriptGit(repo_path, config)

def get_gript_status(repo_path: str = ".") -> Dict[str, Any]:
    """Get the Gript status for a repository."""
    gript_git = GriptGit(repo_path)
    return gript_git.get_gript_info()

def migrate_to_gript(repo_path: str = ".") -> Dict[str, Any]:
    """Migrate an existing repository to use Gript."""
    # Placeholder for migration logic
    gript_git = GriptGit(repo_path)
    return gript_git.get_gript_info()
