import yaml
import hashlib

# https://jira.readthedocs.io/en/master/examples.html
import jira


class Jira(object):
    def __init__(self, **kwargs):
        self.server = kwargs.get("server", "http://127.0.0.1")
        self.project = kwargs.get("project", "PROJECT")
        self.issuetype = kwargs.get("issuetype", "Task")

        self.transition_reopen = kwargs.get("transition_reopen", "Reopen")
        self.resolution_wontfix = kwargs.get("resolution_wontfix", "Won't fix")
        self.updated_in = kwargs.get("issues_updated_in", "1w")

        user = kwargs.get("user", "user")
        password = kwargs.get("password", "password")

        self._auth(user, password, self.server)

    def _auth(self, user, password, server):
        self.client = jira.JIRA(server=server, basic_auth=(user, password))

    def __issue_labels_string(self, data):
        """Extract labels from issue data and for a fingerprint line."""
        labels = data["alerts"][0]["labels"]
        labels_string = ",".join(["=".join((key, val.replace(" ", "_"))) for key, val in labels.items()])
        labels_hash = hashlib.md5(labels_string.encode()).hexdigest()
        return labels_hash

    def issue_create(self, data):
        """Create issue.
        Returns issue ID.
        """
        issue_dict = {
            "project": {"key": self.project},
            "issuetype": {"name": self.issuetype},
            "summary": "Alert: {name} ({values})".format(
                name=data["alerts"][0]["labels"].get("alertname"),
                values=", ".join([val for key, val in data["alerts"][0]["labels"].items() if key != "alertname"]),
            ),
            "labels": [self.__issue_labels_string(data)],
            "description": "{code}" + yaml.dump(data, default_flow_style=False) + "{code}",
        }
        new_issue = self.client.create_issue(fields=issue_dict)
        return new_issue.key

    def issue_find(self, data):
        """Find issue by fingerprint (dict of data which comes from alertmanager).
        Returns issue ID (str) or False.
        """
        labels = self.__issue_labels_string(data)

        if not labels:
            return False

        try:
            issue = self.client.search_issues(
                """project="{project}"
                AND issuetype="{issuetype}"
                AND labels="{labels}"
                AND updated >= -{max_age}
                ORDER BY created DESC""".format(
                    project=self.project, issuetype=self.issuetype, labels=labels, max_age=self.updated_in
                ),
                maxResults=1,
            )
            if len(issue) > 0:
                issue = issue.pop()
        except jira.exceptions.JIRAError:
            issue = False

        return issue

    def issue_update(self, issue_id, data):
        """Update issue.
            Re-open if closed.
            Add a comment if it changed.
            Do nothing if issue is in "Won't Fix" status.
        Returns True if updated, otherwise False.
        """
        issue = self.client.issue(issue_id)

        if issue.fields.resolution and issue.fields.resolution.name == self.resolution_wontfix:
            return False

        # Reopen alert once if there's at least 1 non-"resolved" status
        for alert in data["alerts"]:
            if alert["status"] == "resolved":
                continue

            transitions_available = self.client.transitions(issue)
            for t in transitions_available:
                if t["name"] == self.transition_reopen:
                    self.client.transition_issue(issue, t["id"])

            break

        comments = self.client.comments(issue)
        comment_is_first = len(comments) < 1

        for alert in data["alerts"]:
            text = "{code}" + yaml.dump(alert, default_flow_style=False) + "{code}"
            comment_is_unique = text not in [c.body for c in comments]
            if comment_is_first or comment_is_unique:
                self.client.add_comment(issue, text)

        return True

    def issue_list(self, count=20):
        try:
            issues = self.client.search_issues(
                'project="{project}" AND issuetype={issuetype} order by created desc'.format(
                    project=self.project, issuetype=self.issuetype
                ),
                maxResults=count,
            )
        except jira.exceptions.JIRAError:
            issues = False

        return issues
