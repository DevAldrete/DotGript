import typer
from rich import print
import gript.agents as agents

app = typer.Typer()
app.add_typer(agents.app, name="ai")


@app.command()
def main():
    print("Hello from dotgript!")


@app.command()
def yolo():
    print("Yo!")


if __name__ == "__main__":
    app()
