import getpass
from inspect import signature
import ipaddress
import os
from pathlib import Path
import subprocess
import psutil
import socket  
import typer

import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typer import colors
from log import logger

app = typer.Typer(invoke_without_command=True)


@app.callback()
def default(ctx: typer.Context):
    """
    命令入口。未指定子命令时默认执行 scan。
    """
    if ctx.invoked_subcommand is None:
        pass


@app.command()
def nopass():
    real_user = os.environ.get("SUDO_USER") or getpass.getuser()
    sudoers_file = Path(f"/etc/sudoers.d/{real_user}")
    config_line = f"{real_user} ALL=(ALL) NOPASSWD:ALL\n"

    
    if os.geteuid() != 0:
        typer.secho("❌ 需要 root 权限运行此命令，请使用 sudo:", fg=typer.colors.RED)
        typer.echo("👉 例如：sudo uv run main.py user nopass")
        raise typer.Exit(code=1)

    # 获取实际用户名
    real_user = os.environ.get("SUDO_USER") or getpass.getuser()
    sudoers_file = Path(f"/etc/sudoers.d/{real_user}")
    config_line = f"{real_user} ALL=(ALL) NOPASSWD:ALL\n"

    # 检查是否已经免密
    if is_nopass_configured(real_user):
        typer.secho(f"✅ 用户 {real_user} 已具备 sudo 免密码权限", fg=typer.colors.GREEN)
        return

    # 再检查文件是否已存在（备用）
    if sudoers_file.exists():
        typer.secho(f"⚠️ 发现已存在 sudoers 文件但权限未生效: {sudoers_file}", fg=typer.colors.YELLOW)

    

    if sudoers_file.exists():
        typer.secho(f"✅ Sudo 免密码已配置: {sudoers_file}", fg=typer.colors.GREEN)
        return

    try:
        typer.secho(f"🛠 正在为用户 {real_user} 配置 sudo 免密码权限...", fg=typer.colors.BLUE)
        sudoers_file.write_text(config_line)
        sudoers_file.chmod(0o440)
        typer.secho(f"✅ 配置成功: {sudoers_file}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ 配置失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2)



def is_nopass_configured(user: str) -> bool:
    try:
        result = subprocess.run(
            ["sudo", "-n", "-l", "-U", user],
            capture_output=True,
            text=True,
            check=False
        )
        return "NOPASSWD: ALL" in result.stdout
    except Exception as e:
        typer.echo(f"⚠️ 检查 sudo 权限失败: {e}")
        return False




if __name__ == "__main__":
    app()
