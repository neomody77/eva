#!/usr/bin/env python3
"""
示例：基于 prompt_toolkit 的简易 CLI（非交互式）
用法:
    python cli_ptk.py help            # 列出所有命令
    python cli_ptk.py help greet     # 查看某条命令说明
    python cli_ptk.py greet Alice    # 执行命令
"""
import sys
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import HTML

# --------------------------------------------------------------------------- #
# 配置部分
# --------------------------------------------------------------------------- #
COMMANDS = {
    "help":    ("help [cmd]",      "显示所有命令或查看单个命令的说明"),
    "greet":   ("greet [name]",    "打印问候语"),
    "version": ("version",         "显示程序版本"),
}

# --------------------------------------------------------------------------- #
# 命令实现
# --------------------------------------------------------------------------- #
def show_help(cmd: str | None = None) -> None:
    """
    help 或 help <cmd>
    """
    if cmd is None:
        print_formatted_text(HTML("\n<skyblue>Usage</skyblue>:  cli_ptk.py &lt;command&gt; [args]\n"))
        print_formatted_text(HTML("<u>Available commands</u>:"))
        for name, (syntax, desc) in COMMANDS.items():
            print_formatted_text(
                HTML(f"  <ansiyellow>{syntax:<16}</ansiyellow> {desc}")
            )
    else:
        if cmd in COMMANDS:
            syntax, desc = COMMANDS[cmd]
            print_formatted_text(HTML(f"<ansigreen>{syntax}</ansigreen> — {desc}"))
        else:
            print_formatted_text(HTML(f"<ansired>未知命令: {cmd}</ansired>"))

def greet(args: list[str]) -> None:
    name = args[0] if args else "stranger"
    print_formatted_text(HTML(f"<ansigreen>Hello, {name}!</ansigreen>"))

def version(_args: list[str]) -> None:
    print_formatted_text(HTML("<b>CLI Demo version 0.1.0</b>"))

DISPATCH = {
    "help":    show_help,
    "greet":   greet,
    "version": version,
}

# --------------------------------------------------------------------------- #
# 主入口
# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> None:
    if len(argv) < 2:
        # 没给命令，直接打印用法
        show_help()
        sys.exit(1)

    cmd, *args = argv[1:]
    if cmd == "help":
        show_help(args[0] if args else None)
    elif cmd in DISPATCH:
        try:
            DISPATCH[cmd](args)
        except Exception as exc:
            print_formatted_text(HTML(f"<ansired>执行 {cmd} 出错: {exc}</ansired>"))
    else:
        print_formatted_text(HTML(f"<ansired>未知命令: {cmd}</ansired>"))
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
