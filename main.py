import yaml
import logging
from flask import Flask, request, jsonify

from lib.jira import Jira


with open('./config.yml') as fp:
    config = yaml.load(fp)

jira = Jira(**config['jira'])
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG if config['daemon']['debug'] else logging.WARNING)
app.stats = {
    'events': {
        'firing': 0,
        'resolved': 0,
    },
    'healthcheck': {
        'count': 0,
        'latest': 'pending',
    }
}


@app.route('/')
def index():
    message = """
<pre>
- Alerts should go to "/alert"
  (it's also possible to send them to "/", but for compatibility reasons only)

- Healthcheck located at "/health"

- Statistic is available at "/stats"
</pre>
""".strip()
    return message


@app.route('/', methods=['POST'])  # for compatibility reasons
@app.route('/alert', methods=['POST'])
def alert():
    app.logger.debug("Received an event")

    try:
        event = request.json
    except Exception:
        app.logger.error("Could not parse data: {}".format(request.json))
        return 'Bad Request', 400

    # Event could contain more than 1 alert
    for alert in event['alerts']:
        data = {**event, 'alerts': [alert], 'commonLabels': dict(alert['labels'])}  # form new object with only 1 alert each

        app.stats['events'][data['status']] += 1

        issue = jira.issue_find(data)
        app.logger.debug("Found issue: {}".format(issue))

        if issue:
            app.logger.debug("Updating existing issue")
            jira.issue_update(issue, data)
            if len(event['alerts']) == 1:
                return 'Already Reported', 200
        else:
            app.logger.debug("Creating new issue")
            jira.issue_create(data)
            if len(event['alerts']) == 1:
                return 'Created', 201

    return 'Accepted', 202


@app.route('/health')
def health():
    app.logger.debug("Checking Jira availability by issuing simple search")
    issues = jira.issue_list(count=20)

    if isinstance(issues, list):
        result = "OK"
    else:
        app.logger.error("Could not find issues: {}".format(issues))
        result = "Failed"

    app.stats['healthcheck']['count'] += 1
    app.stats['healthcheck']['latest'] = result

    code = 200 if result == "OK" else 500

    app.logger.debug("Healthcheck result was: {}".format(result))

    return result, code


@app.route('/stats')
def stats():
    return jsonify(app.stats), 200


if __name__ == '__main__':
    app.run(**config['daemon'])
