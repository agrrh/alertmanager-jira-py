from app.app import app
from app.config import config

if __name__ == "__main__":
    app.run(**config["daemon"])
