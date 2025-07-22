import getpass
import os
from pathlib import Path
import subprocess
import typer
import tempfile
import subprocess
import typer
from pathlib import Path
import requests
import requests
import subprocess
import tempfile
import typer
from pathlib import Path
import os
import os
import subprocess
import typer
import getpass

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
def list(ctx: typer.Context):
      typer.echo(f"🚀 list application")


@app.command()
def install(
    name: str = typer.Argument(..., help="应用名称（必填）"),
):
    typer.echo(f"🚀 Installing application: {name}")
    logger.info(f"application install: {name}")
    
    if name == 'docker':
        install_docker()



@app.command()
def uninstall(
    name: str = typer.Argument(..., help="应用名称（必填）"),
):
    typer.echo(f"🚀 uninstall application: {name}")
    logger.info(f"application uninstall: {name}")
    
    if name == 'docker':
        uninstall_docker()   

    





def install_docker():
    typer.echo("🐳 开始使用官方脚本安装 Docker...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        script_path = tmp_path / "get-docker.sh"

        try:
            # 下载安装脚本
            typer.echo(f"📥 下载安装脚本到临时文件: {script_path}")
            resp = requests.get("https://get.docker.com", timeout=10)
            resp.raise_for_status()
            script_path.write_bytes(resp.content)

            # 执行安装脚本（需要 sudo）
            typer.echo("⚙️ 正在执行安装脚本（需要 sudo 权限）...")
            subprocess.run(["sudo", "sh", str(script_path)], check=True)

            typer.secho("✅ Docker 安装完成！", fg=typer.colors.GREEN)

            # 获取实际登录用户
            current_user = os.environ.get("SUDO_USER") or getpass.getuser()

            # 检查是否已经在 docker 组中
            groups_output = subprocess.check_output(["id", current_user], text=True)
            if "docker" not in groups_output:
                typer.echo(f"👤 当前用户 {current_user} 不在 docker 组，正在添加...")
                subprocess.run(["sudo", "usermod", "-aG", "docker", current_user], check=True)
                typer.secho(f"✅ 已将用户 {current_user} 添加到 docker 用户组", fg=typer.colors.GREEN)
                typer.echo("⚠️ 请注销并重新登录后使组权限生效")
            else:
                typer.secho(f"✅ 用户 {current_user} 已在 docker 用户组中", fg=typer.colors.GREEN)

        except requests.RequestException as e:
            typer.secho(f"❌ 下载失败: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        except subprocess.CalledProcessError as e:
            typer.secho(f"❌ 命令执行失败: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=2)
        except Exception as e:
            typer.secho(f"❌ 发生未知错误: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=3)





def detect_os_family():
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            os_info = f.read().lower()
            if "ubuntu" in os_info or "debian" in os_info:
                return "debian"
            elif "centos" in os_info or "rhel" in os_info or "rocky" in os_info:
                return "rhel"
            elif "fedora" in os_info:
                return "fedora"
            elif "alpine" in os_info:
                return "alpine"
    return None


def run(cmd):
    typer.echo(f"💻 {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def uninstall_docker(purge: bool = typer.Option(True, help="是否删除 Docker 数据目录")):
    os_family = detect_os_family()

    if os.geteuid() != 0:
        typer.secho("❌ 需要 sudo 或 root 权限运行此命令", fg=typer.colors.RED)
        raise typer.Exit(1)

    if not os_family:
        typer.secho("❌ 无法识别的 Linux 发行版，不支持自动卸载", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho(f"🔍 检测到系统类型: {os_family}", fg=typer.colors.CYAN)

    try:
        if os_family == "debian":
            run(["apt-get", "purge", "-y", "docker-ce", "docker-ce-cli", "containerd.io",
                 "docker-buildx-plugin", "docker-compose-plugin", "docker.io"])

        elif os_family == "rhel":
            run(["yum", "remove", "-y", "docker-ce", "docker-ce-cli", "containerd.io",
                 "docker-compose-plugin", "docker", "docker-client", "docker-common"])

        elif os_family == "fedora":
            run(["dnf", "remove", "-y", "docker-ce", "docker-ce-cli", "containerd.io",
                 "docker-compose-plugin", "moby-engine", "docker", "docker-client"])

        elif os_family == "alpine":
            run(["apk", "del", "docker", "containerd", "docker-cli"])

        else:
            typer.secho("⚠️ 不支持的系统类型", fg=typer.colors.RED)
            raise typer.Exit(1)

        if purge:
            typer.secho("🧹 清理 Docker 数据目录...", fg=typer.colors.BLUE)
            for path in ["/var/lib/docker", "/var/lib/containerd"]:
                if os.path.exists(path):
                    run(["rm", "-rf", path])

        typer.secho("✅ Docker 卸载完成", fg=typer.colors.GREEN)

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ 执行命令失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(2)



if __name__ == "__main__":
    app()
