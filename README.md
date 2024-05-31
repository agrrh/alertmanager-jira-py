# Info

Adapter to transform Alertmanager events to Jira trackable tasks.

![Diagram](https://private-user-images.githubusercontent.com/1294495/335548376-9139e7fe-40db-418f-ba40-99369a3676ea.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTcxNTI2OTIsIm5iZiI6MTcxNzE1MjM5MiwicGF0aCI6Ii8xMjk0NDk1LzMzNTU0ODM3Ni05MTM5ZTdmZS00MGRiLTQxOGYtYmE0MC05OTM2OWEzNjc2ZWEucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI0MDUzMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNDA1MzFUMTA0NjMyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZjlmMDc4NWIyMmU0NTllNjc0YzFkOTRmODBmYWNjZmJmYzNhMDI4ZjM4MmQ1ZmU4Nzc3NDUzN2Q2NWZmNDhmMCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmYWN0b3JfaWQ9MCZrZXlfaWQ9MCZyZXBvX2lkPTAifQ.sjH5fRcU2c5_bNW0bVwm_RXMCYLWHa60GC-yU2EAYmE)

# Usage

Ready to run as a docker container:

```
docker build . -t agrrh/alertmanager-jira-py:1.0.0
docker run -ti -p 8080:8080 agrrh/alertmanager-jira-py:1.0.0
```

Then send your Alertmanager webhooks to this adapter:

```
receivers:
  - name: "my-alert"
    slack_configs:
      ...
    webhook_configs:
      - url: http://127.0.0.1:8080/alert
```

## Logic summary

- Once alert is triggered, adapter will create new task in your Jira project

- If there's already Jira task created and both conditions satisfied:
  - task closed with any but `resolution_wontfix` resolution
  - task newer than `issues_updated_in` time

  ... then adapter will re-open same task instead of creating new one.

## Testing

One could run tests with following alert data examples:

```
# Firing
http POST 0.0.0.0:5000/alert < samples/firing.json

# Resolved
http POST 0.0.0.0:5000/alert < samples/resolved.json

# Multiple
http POST 0.0.0.0:5000/alert < samples/multiple.json
```

# Alternatives

- https://github.com/free/jiralert - Golang, it inspired my implementation
- https://github.com/fabxc/jiralerts - Python, less flexible IMO
