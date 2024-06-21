# Pull Requests to Confluence

This repository contains a Python script designed to automate the process of retrieving open pull requests from a GitHub repository and publishing the details to a Confluence page. The script leverages the GitHub and Confluence APIs to seamlessly integrate these platforms, ensuring that your team stays updated with the latest pull requests.

## Project Structure

```
pull-requests-to-confluence/
├── config/
│   └── config.yaml.template
├── templates/
│   └── pull-requests.html.template
├── Dockerfile
├── docker/
│   ├── entrypoint.sh
│   ├── run.sh
│   └── crontab
├── main.py
├── requirements.txt
└── pull_request_counts.csv
```

- `config/config.yaml.template`: Template configuration file to be copied and customized with your GitHub and Confluence parameters.
- `templates/pull-requests.html.template`: Template for the HTML content, to be copied and customized.
- `Dockerfile`: Instructions to build the Docker image.
- `docker/`: Directory containing Docker-related files.
  - `entrypoint.sh`: Script to set up and run the container.
  - `run.sh`: Bash script to run the Python script, designed to be called from crontab.
  - `crontab`: File containing cron job definitions for scheduling the script.
- `main.py`: Main script that fetches pull requests and publishes them to Confluence.
- `requirements.txt`: List of dependencies required for the project.
- `pull_request_counts.csv`: CSV file tracking the number of open pull requests by date.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/trustlreis/pull-requests-to-confluence.git
   cd pull-requests-to-confluence
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the template configuration and HTML files to customize:
   ```bash
   cp config/config.yaml.template config/config.yaml
   cp templates/pull-requests.html.template templates/pull-requests.html
   ```

4. Update `config/config.yaml` with your GitHub and Confluence credentials and settings.

## Usage

Run the script:
```bash
python main.py
```

This will fetch the open pull requests from the specified GitHub repository and publish them to the specified Confluence page, along with the generated charts.

## Docker

### Building the Docker Image

1. Navigate to the project directory:
   ```bash
   cd pull-requests-to-confluence
   ```

2. Build the Docker image:
   ```bash
   docker build -t pull-requests-to-confluence .
   ```

### Running the Docker Container

To run the container as a daemon with automatic restart:

1. Run the container:
   ```bash
   docker run -d --restart unless-stopped pull-requests-to-confluence
   ```

### Docker Files

- `Dockerfile`: Contains instructions to build the Docker image, including installing dependencies and copying project files.
- `docker/entrypoint.sh`: Shell script to set up and run the application inside the container.
- `docker/run.sh`: Bash script to run the Python script. This is designed to be scheduled via `crontab` for periodic execution.
- `docker/crontab`: Contains cron job definitions to schedule the script execution.

### Dockerfile Details

The `Dockerfile` sets up the environment to run the Python script on a schedule using cron:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create a working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for cron
RUN apt-get update && apt-get install -y cron

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the crontab file into the cron.d directory
COPY docker/run.sh /usr/local/bin/fetch_pull_requests
COPY docker/crontab /etc/cron.d/fetch_pull_requests

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/fetch_pull_requests
RUN chmod 0755 /usr/local/bin/fetch_pull_requests

# Apply the cron job
RUN crontab /etc/cron.d/fetch_pull_requests

# Create the entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the command on container startup
CMD ["/entrypoint.sh"]
```

### Scheduling with Cron

To schedule the script using cron:

1. Open the crontab configuration:
   ```bash
   crontab -e
   ```

2. Add the following cron job definitions to schedule the script to run 6 times per day on business weekdays:
   ```
   # ┌────────────── minute (0 - 59)
   # │ ┌──────────── hour (0 - 23)
   # │ │ ┌────────── day of the month (1 - 31)
   # │ │ │ ┌──────── month (1 - 12)
   # │ │ │ │ ┌────── day of the week (0 - 6) (Sunday to Saturday)
   # │ │ │ │ │
   # │ │ │ │ │
   0 11,13,16,18,20 * * 1-5 /usr/local/bin/fetch_pull_requests # image is running in UTC
   ```

   The image runs in the UTC time zone. Below is a table converting the schedule to BRT (UTC-3):

   | UTC Time | BRT Time (UTC-3) |
   |----------|------------------|
   | 11:00    | 08:00            |
   | 13:00    | 10:00            |
   | 16:00    | 13:00            |
   | 18:00    | 15:00            |
   | 20:00    | 17:00            |

3. To list the current cron jobs scheduled, use:
   ```bash
   crontab -l
   ```

## License

This project is licensed under the MIT License.
