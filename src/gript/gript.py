from gript.core.gript import GitAutomationSuite
from typer import Typer
from typing import Optional
from rich import print

git_suite = GitAutomationSuite(repo_path=".")

app = Typer()


@app.command("nfeature")
def new_feature(feature_name: str, issue_number: Optional[int] = None):
    branch_name = git_suite.smart_feature_start(
        feature_name=feature_name, issue_number=issue_number
    )
    print(f"You have made a new branch called {branch_name}. Congrats!")


@app.command("ffeature")
def finished_feature(branch_name: str, squash: bool = True):
    git_suite.smart_feature_finish(branch_name=branch_name, squash=squash)
