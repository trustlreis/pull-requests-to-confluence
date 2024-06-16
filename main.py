import requests
from requests.auth import HTTPBasicAuth
from jinja2 import Environment, FileSystemLoader
import os
import yaml

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


def fetch_pull_requests():
    response = requests.get(github_url, headers=github_headers)
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return []


def render_html(pull_requests):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('templates/pull-requests.html')
    return template.render(pull_requests=pull_requests)


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


if __name__ == '__main__':
    pull_requests = fetch_pull_requests()
    if pull_requests:
        html_content = render_html(pull_requests)
        publish_to_confluence(html_content, 'Open Pull Requests')
