from git import Git
from typer import Typer
from rich import print
from typing import Optional
from gript.core.gript import GitAutomationSuite

git_suite = GitAutomationSuite(repo_path=".")

app = Typer()


@app.command("new")
def new(
    feature_name: str,
    issue_number: Optional[int] = None,
    from_branch: Optional[str] = None,
    interactive: bool = False,
):
    branch_info = git_suite.smart_feature_start(
        feature_name=feature_name,
        issue_number=issue_number,
        from_branch=from_branch,
        interactive=interactive,
    )

    if branch_info["success"]:
        print(
            f"✅ You have made a new branch called {branch_info['branch_name']}. Congrats 🎉!"
        )

        if not branch_info["upstream_set"]:
            print("You haven't set it up in GitHub. Watch out for it!")
    else:
        print("⚠️ That branch already exists!")


@app.command("done")
def done(
    branch_name: str,
    squash: bool = True,
    push: bool = True,
    delete_branch: bool = False,
):
    git_suite.smart_feature_finish(
        branch_name=branch_name,
        squash=squash,
        delete_branch=delete_branch,
        push_after_merge=push,
    )
