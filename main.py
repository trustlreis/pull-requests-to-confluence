import requests
from requests.auth import HTTPBasicAuth
from jinja2 import Environment, FileSystemLoader
import os
import yaml
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import base64
from io import BytesIO

# Load configuration from YAML file
with open('config/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Extract GitHub parameters
github_token = config['github']['token']
github_query = config['github']['query']
github_url = config['github']['url'].format(query=github_query)
github_headers = {
    'Authorization': f'token {github_token}',
    'Accept': config['github']['headers']['Accept']
}

# Extract Confluence parameters
confluence_base_url = config['confluence']['base_url']
confluence_space_key = config['confluence']['space_key']
confluence_parent_page_id = config['confluence'].get('parent_page_id')
confluence_auth = HTTPBasicAuth(config['confluence']['auth']['user'], config['confluence']['auth']['token'])

# Path to the CSV file
csv_file_path = 'pull_request_counts.csv'


def fetch_pull_requests():
    response = requests.get(github_url, headers=github_headers)
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return []


def update_csv_with_pr_count(pull_requests):
    now = datetime.now().strftime('%Y-%m-%d')
    pr_count = len(pull_requests)

    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
    else:
        df = pd.DataFrame(columns=['date_time', 'pull_request_count'])

    if now in df['date_time'].values:
        df.loc[df['date_time'] == now, 'pull_request_count'] = pr_count
    else:
        new_row = pd.DataFrame({'date_time': [now], 'pull_request_count': [pr_count]})
        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(csv_file_path, index=False)
    return df


def filter_last_15_days(data_frame):
    now = datetime.now()
    fifteen_days_ago = now - timedelta(days=15)
    data_frame['date_time'] = pd.to_datetime(data_frame['date_time'])
    filtered_df = data_frame[data_frame['date_time'] >= fifteen_days_ago]
    filtered_df['date_time'] = filtered_df['date_time'].dt.strftime('%Y-%m-%d')
    return filtered_df


def render_html(pull_requests, pull_request_count, open_pr_chart_base64, pr_size_chart_base64, gh_query):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('templates/pull-requests.html')
    return template.render(
        pull_requests=pull_requests,
        pull_request_count=pull_request_count,
        open_pr_chart_base64=open_pr_chart_base64,
        pr_size_chart_base64=pr_size_chart_base64,
        gh_query=gh_query
    )


def get_page_id_and_version(title):
    url = f"{confluence_base_url}/rest/api/content"
    params = {
        'title': title,
        'spaceKey': confluence_space_key,
        'expand': 'version'
    }
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, params=params, auth=confluence_auth)
    if response.status_code == 200:
        results = response.json()['results']
        if results:
            page = results[0]
            return page['id'], page['version']['number']
    return None, None


def publish_to_confluence(content, title):
    page_id, version = get_page_id_and_version(title)
    url = f"{confluence_base_url}/rest/api/content"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'type': 'page',
        'title': title,
        'space': {'key': confluence_space_key},
        'body': {
            'storage': {
                'value': content,
                'representation': 'storage'
            }
        }
    }
    if confluence_parent_page_id:
        data['ancestors'] = [{'id': confluence_parent_page_id}]

    if page_id:
        url = f"{confluence_base_url}/rest/api/content/{page_id}"
        data['version'] = {'number': version + 1}
        response = requests.put(url, json=data, headers=headers, auth=confluence_auth)
    else:
        response = requests.post(url, json=data, headers=headers, auth=confluence_auth)

    if response.status_code in (200, 201):
        print("Page published successfully.")
    else:
        print(f"Failed to publish page: {response.status_code} - {response.text}")


def create_bar_chart(data_frame):
    filtered_df = filter_last_15_days(data_frame)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(filtered_df['date_time'], filtered_df['pull_request_count'], color='skyblue', edgecolor='black')
    plt.xlabel('Date')
    plt.ylabel('Number of Open Pull Requests')
    plt.title('Open Pull Requests by Date (Last 15 Days)')
    plt.xticks(rotation=45)

    # Add text annotations
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def create_pie_chart(label_sizes):
    label_size_counts = Counter(label_sizes)
    plt.figure(figsize=(8, 8))
    plt.pie(label_size_counts.values(), labels=label_size_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Pull Requests Grouped by Label Size')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def create_charts(pull_requests):
    label_sizes = [label['name'] for pr in pull_requests for label in pr['labels'] if
                   label['name'].startswith('pr_size_')]

    updated_df = update_csv_with_pr_count(pull_requests)
    open_pr_chart_base64 = create_bar_chart(updated_df)
    pr_size_chart_base64 = create_pie_chart(label_sizes)

    return open_pr_chart_base64, pr_size_chart_base64

if __name__ == '__main__':
    pull_requests = fetch_pull_requests()
    if pull_requests:
        pull_request_count = len(pull_requests)
        open_pr_chart_base64, pr_size_chart_base64 = create_charts(pull_requests)
        html_content = render_html(pull_requests, pull_request_count, open_pr_chart_base64, pr_size_chart_base64, github_query)
        publish_to_confluence(html_content, 'Open Pull Requests')