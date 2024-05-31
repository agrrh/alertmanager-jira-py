from flask import request

from app.app import app
from app.jira import jira


@app.route("/", methods=["POST"])  # for compatibility reasons
@app.route("/alert", methods=["POST"])
def alert():
    app.logger.debug("Received an event")

    try:
        event = request.json
    except Exception:
        app.logger.error("Could not parse data: {}".format(request.json))
        return "Bad Request", 400

    # Event could contain more than 1 alert
    for alert in event["alerts"]:
        data = {
            **event,
            "alerts": [alert],
            "commonLabels": dict(alert["labels"]),
        }  # form new object with only 1 alert each

        app.stats["events"][data["status"]] += 1

        issue = jira.issue_find(data)
        app.logger.debug("Found issue: {}".format(issue))

        if issue:
            app.logger.debug("Updating existing issue")
            jira.issue_update(issue, data)
            if len(event["alerts"]) == 1:
                return "Already Reported", 200
        else:
            app.logger.debug("Creating new issue")
            jira.issue_create(data)
            if len(event["alerts"]) == 1:
                return "Created", 201

    return "Accepted", 202
