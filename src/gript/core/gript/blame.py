"""
Gript Git Blame Module
This module provides functions for blaming files in a Git repository.
"""
from typing import List, Dict, Union
from git import Repo, GitCommandError
from .errors import _handle_git_error

def blame_file(repo: Repo, file_path: str) -> Dict[str, Union[str, List[Dict]]]:
    """
    Get blame information for a specific file.
    
    :param repo: The Repo object to get blame info from.
    :param file_path: Path to the file.
    :return: Dictionary with blame information.
    """
    try:
        blame_info = repo.blame(rev='HEAD', file=file_path)
        
        blame_list = []
        for commit, lines in blame_info:
            blame_list.append({
                "commit": commit.hexsha,
                "author": commit.author.name,
                "date": commit.authored_datetime.isoformat(),
                "lines": lines
            })
            
        return {"file_path": file_path, "blame": blame_list}
    except GitCommandError as e:
        raise _handle_git_error("blame_file", e)
