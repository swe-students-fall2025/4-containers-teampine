# pylint: disable=RULE1, RULE2, RULE3
from flask import Flask


def create_app():
    app = Flask(__name__)
    return app
