# -*- coding: utf-8 -*-
from os.path import join
import pkg_resources

from flask import Flask

from .settings import DefaultConfig


def create_app(config_object=None):
    """Application factory.

    Explained in greater detail here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    """
    sprefix = pkg_resources.resource_filename("pybamview", "")
    app = Flask(__name__, static_folder=join(sprefix, "data"),
                template_folder=join(sprefix, "data", "templates"))

    configure_app(app, config_obj=config_object)
    configure_template_filters(app)

    return app


def configure_app(app, config_obj=None):
    """Configure the app in different ways."""
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(config_obj or DefaultConfig)


def configure_template_filters(app):
    """Configure custom Jinja2 template filters."""

    @app.template_filter()
    def isnuc(x):
        return str(x).upper() in ["A", "C", "G", "T"]
