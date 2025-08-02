"""
Gript Git Repository Module
This module provides functions for initializing and inspecting Git repositories.
"""
from typing import List, Dict
from git import Repo, GitCommandError
from .errors import _handle_git_error

def init_repo(path: str, bare: bool = False) -> Repo:
    """
    Initialize a new Git repository.
    
    :param path: Path where to initialize the repository.
    :param bare: Whether to create a bare repository.
    :return: The initialized Repo object.
    """
    try:
        repo = Repo.init(path, bare=bare)
        return repo
    except GitCommandError as e:
        raise _handle_git_error("init_repo", e)

def clone_repo(repo_url: str, dest_dir: str) -> Repo:
    """
    Clone a Git repository from the given URL to the specified destination directory.
    
    :param repo_url: URL of the repository to clone.
    :param dest_dir: Directory where the repository will be cloned.
    :return: The cloned Repo object.
    """
    try:
        repo = Repo.clone_from(repo_url, dest_dir)
        return repo
    except GitCommandError as e:
        raise _handle_git_error("clone_repo", e)

def get_repo_status(repo: Repo) -> Dict[str, List[str]]:
    """
    Get the status of the working directory of the given repository.
    
    :param repo: The Repo object to check.
    :return: A dictionary with categorized file statuses.
    """
    try:
        status = {
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")]
        }
        return status
    except GitCommandError as e:
        raise _handle_git_error("get_repo_status", e)

def get_repo_info(repo: Repo) -> str:
    """
    Get basic information about the repository.
    
    :param repo: The Repo object to get information from.
    :return: A string containing the repository's URL and current branch.
    """
    return f"Repository URL: {repo.remotes.origin.url}, Current Branch: {repo.active_branch.name}"
