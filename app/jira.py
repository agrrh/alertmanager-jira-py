from lib.jira import Jira

from app.config import config

jira = Jira(**config["jira"])
