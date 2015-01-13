# -*- coding: utf-8 -*-
from flask import Flask

from .settings import DefaultConfig
from . import browser

# Common blueprints
DEFAULT_BLUEPRINTS = (browser.blueprint,)


def create_app(config_object=None, blueprints=None):
    """Application factory.

    Explained in greater detail here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    """
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(__name__, template_folder="browser/templates",
                static_folder="browser/static")

    configure_app(app, config_obj=config_object)
    register_blueprints(app, blueprints=blueprints)
    configure_template_filters(app)

    return app


def configure_app(app, config_obj=None):
    """Configure the app in different ways."""
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(config_obj or DefaultConfig)


def register_blueprints(app, blueprints):
    """Register blueprints."""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    """Configure custom Jinja2 template filters."""

    @app.template_filter()
    def isnuc(x):
        return str(x).upper() in ["A", "C", "G", "T"]
