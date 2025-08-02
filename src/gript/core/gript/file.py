"""
Gript Git File Module
This module provides functions for interacting with files in a Git repository.
"""
from typing import List
from git import Repo, GitCommandError
from .errors import _handle_git_error

def get_untracked_files(repo: Repo) -> List[str]:
    """
    Get list of untracked files in the repository.
    
    :param repo: The Repo object to check for untracked files.
    :return: List of untracked file paths.
    """
    try:
        return repo.untracked_files
    except GitCommandError as e:
        raise _handle_git_error("get_untracked_files", e)

def add_files(repo: Repo, files: List[str]) -> None:
    """
    Add files to the staging area.
    
    :param repo: The Repo object to add files to.
    :param files: List of file paths to add.
    """
    try:
        repo.index.add(files)
    except GitCommandError as e:
        raise _handle_git_error("add_files", e)

def remove_files(repo: Repo, files: List[str], cached: bool = False) -> None:
    """
    Remove files from the repository or staging area.
    
    :param repo: The Repo object to remove files from.
    :param files: List of file paths to remove.
    :param cached: Whether to only remove from staging area (keep in working dir).
    """
    try:
        args = ["--cached"] if cached else []
        repo.index.remove(files, *args)
    except GitCommandError as e:
        raise _handle_git_error("remove_files", e)

def get_file_content(repo: Repo, file_path: str, commit_ref: str = "HEAD") -> str:
    """
    Get the content of a file at a specific commit.
    
    :param repo: The Repo object to get file content from.
    :param file_path: Path to the file.
    :param commit_ref: Reference to the commit.
    :return: File content as string.
    """
    try:
        commit = repo.commit(commit_ref)
        blob = commit.tree / file_path
        return blob.data_stream.read().decode('utf-8')
    except GitCommandError as e:
        raise _handle_git_error("get_file_content", e)
    except KeyError:
        raise _handle_git_error("get_file_content", GitCommandError("get_file_content", f"File '{file_path}' not found in commit '{commit_ref}'."))
