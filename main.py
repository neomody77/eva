import typer
import sys
 
from commands import register_sub_commands
from log import logger

app = typer.Typer()


register_sub_commands(app)

@app.command()
def greet(name: str):
    """
    打招呼的命令
    """
    typer.echo(f"Hello {name}!")

if __name__ == "__main__":
    if len(sys.argv) == 1:  # 如果没有传递任何命令
        sys.argv.append('--help')  # 强制调用 help
    app()
