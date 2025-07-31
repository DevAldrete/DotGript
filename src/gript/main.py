import typer
from rich import print
from gript.agents import app as AgentApp
from gript.branches import app as BranchApp
from gript.gript_git import app as GitApp 

app = typer.Typer()
app.add_typer(AgentApp, name="ai")
app.add_typer(BranchApp, name="branches")
app.add_typer(GitApp, name="git")


@app.command()
def main():
    print("Hello from dotgript!")


@app.command()
def yolo():
    print("Yo!")


if __name__ == "__main__":
    app()
