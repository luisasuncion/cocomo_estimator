from flask import Flask

from config import Config
from .services import format_currency


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    app.jinja_env.filters["currency_amount"] = format_currency

    from .routes import bp

    app.register_blueprint(bp)
    return app
