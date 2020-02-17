build:
	docker build . -t agrrh/alertmanager-jira-py:dev

release: build
	docker push agrrh/alertmanager-jira-py:dev
