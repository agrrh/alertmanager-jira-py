from app.app import app


@app.route("/")
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
