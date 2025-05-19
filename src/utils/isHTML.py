import re


def is_html(text: str) -> bool:
    html_pattern = re.compile(r"<[^>]+>|&[a-z]+;")
    return bool(html_pattern.search(text))
