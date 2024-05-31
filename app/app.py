import logging
from flask import Flask

from app.config import config


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG if config["daemon"]["debug"] else logging.WARNING)
app.stats = {
    "events": {
        "firing": 0,
        "resolved": 0,
    },
    "healthcheck": {
        "count": 0,
        "latest": "pending",
    },
}
