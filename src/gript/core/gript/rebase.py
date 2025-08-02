"""
Gript Git Rebase Module
This module provides functions for rebasing in a Git repository.
"""
from typing import Dict
from git import Repo, GitCommandError
from .errors import _handle_git_error

def rebase_interactive(repo: Repo, 
                      base_commit: str,
                      continue_rebase: bool = False,
                      abort_rebase: bool = False,
                      skip_commit: bool = False) -> Dict[str, str]:
    """
    Perform an interactive rebase.
    
    :param repo: The Repo object to perform rebase in.
    :param base_commit: The commit to rebase onto.
    :param continue_rebase: Continue an in-progress rebase.
    :param abort_rebase: Abort an in-progress rebase.
    :param skip_commit: Skip the current commit during rebase.
    :return: Dictionary with rebase operation details.
    """
    try:
        args = []
        if continue_rebase:
            args.append("--continue")
        elif abort_rebase:
            args.append("--abort")
        elif skip_commit:
            args.append("--skip")
        else:
            args.append("-i")
            args.append(base_commit)
            
        rebase_output = repo.git.rebase(*args)
        return {"status": "success", "output": rebase_output}
    except GitCommandError as e:
        raise _handle_git_error("rebase_interactive", e)
