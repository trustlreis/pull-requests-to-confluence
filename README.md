# Fetch and Publish GitHub Pull Requests

This repository contains a Python script designed to automate the process of retrieving open pull requests from a GitHub repository and publishing the details to a Confluence page. The script leverages the GitHub and Confluence APIs to seamlessly integrate these platforms, ensuring that your team stays updated with the latest pull requests.

## Features

* **Automated Retrieval**: Fetch open pull requests from your specified GitHub repository.
* **HTML Rendering**: Use Jinja2 templates to render the pull request details into an HTML format.
* **Confluence Publishing**: Automatically publish the rendered HTML content to a specified Confluence page.
* **Scheduled Execution**: Use cron jobs to schedule the script to run at specified intervals.

## Requirements

* Python 3.9+
* GitHub Personal Access Token
* Confluence API Token
* Docker to deploy the scheduler

## Project Structure

```
.
├── config
│   └── config.yaml.template
├── docker
│   ├── crontab
│   └── entrypoint.sh
├── template
│   └── pull-requests.html
├── .gitignore
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

## Configuration

### config.yaml

The `config/config.yaml` file contains configuration for GitHub and Confluence:

```yaml
github:
  token: 'YOUR_GITHUB_TOKEN'
  query: 'is:open is:pr review-requested:username review-requested:anotherusername archived:false'
  url: 'https://api.github.com/search/issues?q={query}&sort=created&order=asc'
  headers:
    Accept: 'application/vnd.github.v3+json'

confluence:
  base_url: 'https://yourconfluence.atlassian.net/wiki'
  space_key: 'YOUR_SPACE_KEY'
  parent_page_id: 'YOUR_PARENT_PAGE_ID'  # Optional
  auth:
    user: 'YOUR_CONFLUENCE_USER'
    token: 'YOUR_CONFLUENCE_API_TOKEN'
```

### template.html

The `template/pull-requests.html` file contains the HTML template for rendering the pull requests.

### crontab

The `docker/crontab` file specifies the cron schedule:

```cron
# ┌────────────── minute (0 - 59)
# │ ┌──────────── hour (0 - 23)
# │ │ ┌────────── day of the month (1 - 31)
# │ │ │ ┌──────── month (1 - 12)
# │ │ │ │ ┌────── day of the week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │
# │ │ │ │ │
  0 8,10,13,15,17 * * 1-5 /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1
```

### entrypoint.sh

The `docker/entrypoint.sh` script starts the cron service and keeps the container running:

```sh
#!/bin/bash

# Start the cron service
service cron start

# Tail the cron log to keep the container running
tail -f /var/log/cron.log
```

## Docker Setup

### Building the Docker Image

To build the Docker image, run the following command from the project root directory:

```sh
docker build -t fetch_pull_requests .
```

### Running the Docker Container

To run the Docker container, execute the following command:

```sh
docker run -d --name fetch_pull_requests_container fetch_pull_requests
```

This will start a Docker container that uses cron to run the `fetch_and_publish.py` script at 8am, 10am, 1pm, 3pm, and 5pm every Monday through Friday. The output will be logged to `/var/log/cron.log` inside the container.

## Dependencies

The `requirements.txt` file lists the Python dependencies:

```text
requests
jinja2
pyyaml
```

Ensure these dependencies are installed within the Docker container by specifying them in the `requirements.txt` file.

## Usage

1. **Configure GitHub and Confluence settings**: Copy `config/config.yaml.template` to `config/config.yaml` and update this file with your GitHub and Confluence credentials and settings.
2. **Build the Docker image**: Run `docker build -t fetch_pull_requests .`.
3. **Run the Docker container**: Execute `docker run -d --name fetch_pull_requests_container fetch_pull_requests`.

The script will automatically fetch open pull requests, render them into HTML, and publish the content to Confluence according to the specified cron schedule.

## License

This project is licensed under the MIT License.
```

This `README.md` file provides a comprehensive overview of the project, including the directory structure, configuration details, and instructions for building and running the Docker container. Adjust the placeholders in the configuration section with your actual credentials and settings.