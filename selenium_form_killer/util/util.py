from urllib.parse import urljoin, urlparse


def get_base_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc


def join_url_action(url, action):
    return urljoin(url, action)
