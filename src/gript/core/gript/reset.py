"""
Gript Git Reset Module
This module provides functions for resetting changes in a Git repository.
"""
from typing import List, Optional, Dict, Union
from git import Repo, GitCommandError
from .errors import _handle_git_error

def reset_repo(repo: Repo, 
              mode: str = "mixed", 
              commit_ref: str = "HEAD",
              paths: Optional[List[str]] = None) -> Dict[str, Union[str, List[str]]]:
    """
    Reset the repository to a specific commit or reset specific files.
    
    :param repo: The Repo object to reset.
    :param mode: Reset mode ('soft', 'mixed', 'hard').
    :param commit_ref: Reference to reset to.
    :param paths: Specific files to reset (if provided, mode is ignored).
    :return: Dictionary with reset operation details.
    """
    try:
        if paths:
            repo.git.reset(commit_ref, "--", *paths)
            return {"status": "success", "reset_paths": paths}
        else:
            repo.git.reset(f"--{mode}", commit_ref)
            return {"status": "success", "reset_mode": mode, "commit_ref": commit_ref}
    except GitCommandError as e:
        raise _handle_git_error("reset_repo", e)
