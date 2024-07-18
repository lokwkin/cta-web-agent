import re

def normalize_url(url):
    # Remove the protocol (http://, https://, etc.)
    url = re.sub(r'^https?://', '', url)
    
    # Remove www. if present
    url = re.sub(r'^www\.', '', url)
    
    # Remove non-alphanumeric characters and convert to lowercase
    normalized = re.sub(r'[^a-zA-Z0-9]', '', url).lower()
    
    return normalized