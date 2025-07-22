
from typer import Typer
from .proxy import app as proxy_app
from .user import app as user_app
from .app import app as app_app


def register_sub_commands(app: Typer):
    app.add_typer(proxy_app, name="proxy")
    app.add_typer(user_app, name='user')
    app.add_typer(app_app, name="app")