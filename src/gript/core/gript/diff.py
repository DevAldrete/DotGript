"""
Gript Git Diff Module
This module provides functions for viewing differences in a Git repository.
"""
from typing import Optional, List, Dict, Union
from git import Repo, GitCommandError
from .errors import _handle_git_error

def get_diff(repo: Repo, 
            cached: bool = False, 
            commit1: Optional[str] = None, 
            commit2: Optional[str] = None,
            file_path: Optional[str] = None,
            context_lines: int = 3,
            word_diff: bool = False) -> Dict[str, Union[str, List[Dict]]]:
    """
    Get differences between commits, staging area, or working directory.
    
    :param repo: The Repo object to get differences from.
    :param cached: Show differences between staging area and last commit.
    :param commit1: First commit to compare (if None, uses HEAD).
    :param commit2: Second commit to compare (if None, uses working dir).
    :param file_path: Specific file to show diff for.
    :param context_lines: Number of context lines to show.
    :param word_diff: Show word-level differences.
    :return: Dictionary with diff information and file changes.
    """
    try:
        diff_args = []
        if cached:
            diff_args.append("--cached")
        if commit1:
            diff_args.append(commit1)
        if commit2:
            diff_args.append(commit2)
        if file_path:
            diff_args.append("--")
            diff_args.append(file_path)
        if context_lines != 3:
            diff_args.append(f"-U{context_lines}")
        if word_diff:
            diff_args.append("--word-diff")
            
        diff_output = repo.git.diff(*diff_args)
        
        # For simplicity, returning raw diff. Parsing can be added if needed.
        return {"diff": diff_output}
    except GitCommandError as e:
        raise _handle_git_error("get_diff", e)
