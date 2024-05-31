from app.app import app
from app.jira import jira


@app.route("/health")
def health():
    app.logger.debug("Checking Jira availability by issuing simple search")
    issues = jira.issue_list(count=20)

    if isinstance(issues, list):
        result = "OK"
    else:
        app.logger.error("Could not find issues: {}".format(issues))
        result = "Failed"

    app.stats["healthcheck"]["count"] += 1
    app.stats["healthcheck"]["latest"] = result

    code = 200 if result == "OK" else 500

    app.logger.debug("Healthcheck result was: {}".format(result))

    return result, code
