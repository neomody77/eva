from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings

from commands.proxy import ProxyCommand

# 设置键盘绑定
bindings = KeyBindings()


@bindings.add('c-q')  # 按 Ctrl-Q 退出
def _(event):
    event.app.exit()


# 主命令行应用
def main():
    # 通过命令实现
    application = Application(
        layout=None,  # 使用默认布局
        key_bindings=bindings,
        full_screen=True
    )
    proxy_command = ProxyCommand()  # 加载 proxy 子命令
    proxy_command.run()

    application.run()


if __name__ == "__main__":
    main()
