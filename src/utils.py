import re
import tldextract


def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.subdomain}.{ext.domain}.{ext.suffix}"


def normalize_url(url):
    # Remove the protocol (http://, https://, etc.)
    url = re.sub(r'^https?://', '', url)

    # Remove www. if present
    url = re.sub(r'^www\.', '', url)

    # Remove non-alphanumeric characters and convert to lowercase
    normalized = re.sub(r'[^a-zA-Z0-9]', '', url).lower()

    return normalized
